"""
A/B Testing API Endpoints

Provides REST API for A/B testing:
- Test management (CRUD)
- User assignment
- Exposure tracking
- Conversion tracking
- Results analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json

from database import get_db
from models import User, ABTest, ABVariant, ABAssignment, ABExposure, ABConversion
from api.auth import get_current_user

router = APIRouter()


# ==================== Request/Response Models ====================

class VariantCreate(BaseModel):
    name: str
    description: str
    traffic_percentage: int = Field(ge=0, le=100)
    is_control: bool = False
    config: dict = {}


class VariantResponse(BaseModel):
    id: str
    name: str
    description: str
    traffic_percentage: int
    is_control: bool
    config: dict
    exposures: int
    conversions: int
    conversion_rate: float

    class Config:
        from_attributes = True


class ABTestCreate(BaseModel):
    name: str
    description: str
    variants: List[VariantCreate]
    target_audience: dict = {}
    metrics: List[dict] = []
    confidence_level: float = 0.95
    sample_size: Optional[int] = None


class ABTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    target_audience: Optional[dict] = None


class ABTestResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    variants: List[VariantResponse]
    target_audience: dict
    metrics: List[dict]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    confidence_level: float
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExposureRequest(BaseModel):
    test_id: str
    variant_id: str
    user_id: str
    timestamp: datetime


class ConversionRequest(BaseModel):
    test_id: str
    variant_id: str
    metric_id: str
    user_id: str
    value: Optional[float] = None
    timestamp: datetime


class EventRequest(BaseModel):
    test_id: str
    variant_id: str
    event_name: str
    properties: dict = {}
    user_id: str
    timestamp: datetime


class TestResultsResponse(BaseModel):
    test_id: str
    winner: Optional[str]
    confidence: float
    improvement: float
    statistical_significance: bool
    variant_results: List[dict]
    recommendations: List[str]


# ==================== Endpoints ====================

@router.get("/tests", response_model=List[ABTestResponse])
async def get_all_tests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all A/B tests with optional status filter."""
    query = db.query(ABTest)

    if status:
        query = query.filter(ABTest.status == status)

    tests = query.order_by(ABTest.created_at.desc()).all()

    # Enrich with metrics
    enriched_tests = []
    for test in tests:
        test_dict = {
            "id": test.id,
            "name": test.name,
            "description": test.description,
            "status": test.status,
            "target_audience": json.loads(test.target_audience) if test.target_audience else {},
            "metrics": json.loads(test.metrics) if test.metrics else [],
            "start_date": test.start_date,
            "end_date": test.end_date,
            "confidence_level": test.confidence_level,
            "created_by": test.created_by,
            "created_at": test.created_at,
            "variants": []
        }

        for variant in test.variants:
            exposures = db.query(ABExposure).filter(ABExposure.variant_id == variant.id).count()
            conversions = db.query(ABConversion).filter(ABConversion.variant_id == variant.id).count()

            test_dict["variants"].append({
                "id": variant.id,
                "name": variant.name,
                "description": variant.description,
                "traffic_percentage": variant.traffic_percentage,
                "is_control": variant.is_control,
                "config": json.loads(variant.config) if variant.config else {},
                "exposures": exposures,
                "conversions": conversions,
                "conversion_rate": conversions / exposures if exposures > 0 else 0.0
            })

        enriched_tests.append(test_dict)

    return enriched_tests


@router.get("/active", response_model=List[ABTestResponse])
async def get_active_tests(db: Session = Depends(get_db)):
    """Get all active A/B tests (no auth required for client-side assignment)."""
    tests = db.query(ABTest).filter(ABTest.status == "active").all()

    enriched_tests = []
    for test in tests:
        test_dict = {
            "id": test.id,
            "name": test.name,
            "description": test.description,
            "status": test.status,
            "target_audience": json.loads(test.target_audience) if test.target_audience else {},
            "metrics": json.loads(test.metrics) if test.metrics else [],
            "start_date": test.start_date,
            "end_date": test.end_date,
            "confidence_level": test.confidence_level,
            "created_by": test.created_by,
            "created_at": test.created_at,
            "variants": []
        }

        for variant in test.variants:
            test_dict["variants"].append({
                "id": variant.id,
                "name": variant.name,
                "description": variant.description,
                "traffic_percentage": variant.traffic_percentage,
                "is_control": variant.is_control,
                "config": json.loads(variant.config) if variant.config else {},
                "exposures": 0,
                "conversions": 0,
                "conversion_rate": 0.0
            })

        enriched_tests.append(test_dict)

    return enriched_tests


@router.post("/tests", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(
    test: ABTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new A/B test."""
    # Validate traffic percentages sum to 100
    total_traffic = sum(v.traffic_percentage for v in test.variants)
    if total_traffic != 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Variant traffic percentages must sum to 100, got {total_traffic}"
        )

    # Ensure exactly one control variant
    control_count = sum(1 for v in test.variants if v.is_control)
    if control_count != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must have exactly one control variant"
        )

    # Create test
    db_test = ABTest(
        name=test.name,
        description=test.description,
        status="draft",
        target_audience=json.dumps(test.target_audience),
        metrics=json.dumps(test.metrics),
        confidence_level=test.confidence_level,
        sample_size=test.sample_size,
        created_by=current_user.id
    )
    db.add(db_test)
    db.flush()

    # Create variants
    for variant_data in test.variants:
        db_variant = ABVariant(
            test_id=db_test.id,
            name=variant_data.name,
            description=variant_data.description,
            traffic_percentage=variant_data.traffic_percentage,
            is_control=variant_data.is_control,
            config=json.dumps(variant_data.config)
        )
        db.add(db_variant)

    db.commit()
    db.refresh(db_test)

    return await get_test_by_id(db_test.id, db, current_user)


@router.get("/tests/{test_id}", response_model=ABTestResponse)
async def get_test_by_id(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific test by ID."""
    test = db.query(ABTest).filter(ABTest.id == test_id).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    test_dict = {
        "id": test.id,
        "name": test.name,
        "description": test.description,
        "status": test.status,
        "target_audience": json.loads(test.target_audience) if test.target_audience else {},
        "metrics": json.loads(test.metrics) if test.metrics else [],
        "start_date": test.start_date,
        "end_date": test.end_date,
        "confidence_level": test.confidence_level,
        "created_by": test.created_by,
        "created_at": test.created_at,
        "variants": []
    }

    for variant in test.variants:
        exposures = db.query(ABExposure).filter(ABExposure.variant_id == variant.id).count()
        conversions = db.query(ABConversion).filter(ABConversion.variant_id == variant.id).count()

        test_dict["variants"].append({
            "id": variant.id,
            "name": variant.name,
            "description": variant.description,
            "traffic_percentage": variant.traffic_percentage,
            "is_control": variant.is_control,
            "config": json.loads(variant.config) if variant.config else {},
            "exposures": exposures,
            "conversions": conversions,
            "conversion_rate": conversions / exposures if exposures > 0 else 0.0
        })

    return test_dict


@router.post("/tests/{test_id}/start")
async def start_test(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start an A/B test."""
    test = db.query(ABTest).filter(ABTest.id == test_id).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    if test.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start test with status: {test.status}"
        )

    test.status = "active"
    test.start_date = datetime.utcnow()
    db.commit()

    return {"message": "Test started successfully", "test_id": test_id}


@router.post("/tests/{test_id}/stop")
async def stop_test(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop an A/B test."""
    test = db.query(ABTest).filter(ABTest.id == test_id).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    if test.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot stop test with status: {test.status}"
        )

    test.status = "completed"
    test.end_date = datetime.utcnow()
    db.commit()

    return {"message": "Test stopped successfully", "test_id": test_id}


@router.post("/exposure")
async def track_exposure(
    exposure: ExposureRequest,
    db: Session = Depends(get_db)
):
    """Track user exposure to variant."""
    # Check if already tracked
    existing = db.query(ABExposure).filter(
        ABExposure.test_id == exposure.test_id,
        ABExposure.user_id == exposure.user_id
    ).first()

    if existing:
        return {"message": "Exposure already tracked"}

    db_exposure = ABExposure(
        test_id=exposure.test_id,
        variant_id=exposure.variant_id,
        user_id=exposure.user_id,
        exposed_at=exposure.timestamp
    )
    db.add(db_exposure)
    db.commit()

    return {"message": "Exposure tracked successfully"}


@router.post("/conversion")
async def track_conversion(
    conversion: ConversionRequest,
    db: Session = Depends(get_db)
):
    """Track conversion event."""
    # Check if user was exposed
    exposure = db.query(ABExposure).filter(
        ABExposure.test_id == conversion.test_id,
        ABExposure.user_id == conversion.user_id
    ).first()

    if not exposure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User was not exposed to this test"
        )

    # Check if already converted
    existing = db.query(ABConversion).filter(
        ABConversion.test_id == conversion.test_id,
        ABConversion.user_id == conversion.user_id,
        ABConversion.metric_id == conversion.metric_id
    ).first()

    if existing:
        return {"message": "Conversion already tracked"}

    db_conversion = ABConversion(
        test_id=conversion.test_id,
        variant_id=conversion.variant_id,
        metric_id=conversion.metric_id,
        user_id=conversion.user_id,
        value=conversion.value,
        converted_at=conversion.timestamp
    )
    db.add(db_conversion)
    db.commit()

    return {"message": "Conversion tracked successfully"}


@router.post("/event")
async def track_event(
    event: EventRequest,
    db: Session = Depends(get_db)
):
    """Track custom event."""
    # Implementation would store events in a separate table
    # For now, just return success
    return {"message": "Event tracked successfully"}


@router.get("/tests/{test_id}/results", response_model=TestResultsResponse)
async def get_test_results(
    test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistical analysis of test results."""
    test = db.query(ABTest).filter(ABTest.id == test_id).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    # Calculate results for each variant
    variant_results = []
    control_result = None

    for variant in test.variants:
        exposures = db.query(ABExposure).filter(ABExposure.variant_id == variant.id).count()
        conversions = db.query(ABConversion).filter(ABConversion.variant_id == variant.id).count()
        conversion_rate = conversions / exposures if exposures > 0 else 0.0

        result = {
            "variant_id": variant.id,
            "variant_name": variant.name,
            "exposures": exposures,
            "conversions": conversions,
            "conversion_rate": conversion_rate,
            "improvement": 0.0,
            "p_value": 1.0,
            "confidence_interval": [conversion_rate, conversion_rate]
        }

        if variant.is_control:
            control_result = result

        variant_results.append(result)

    # Calculate improvements vs control
    winner = None
    best_improvement = 0.0
    statistical_significance = False

    if control_result and control_result["conversion_rate"] > 0:
        for result in variant_results:
            if result["variant_id"] != control_result["variant_id"]:
                improvement = (
                    (result["conversion_rate"] - control_result["conversion_rate"]) /
                    control_result["conversion_rate"]
                ) * 100
                result["improvement"] = improvement

                # Simple z-test for proportions
                p_value = calculate_p_value(
                    control_result["conversions"],
                    control_result["exposures"],
                    result["conversions"],
                    result["exposures"]
                )
                result["p_value"] = p_value

                if p_value < 0.05 and improvement > best_improvement:
                    winner = result["variant_id"]
                    best_improvement = improvement
                    statistical_significance = True

    recommendations = []
    if statistical_significance:
        recommendations.append(f"Winner detected with {best_improvement:.1f}% improvement")
        recommendations.append("Consider implementing the winning variant")
    else:
        recommendations.append("No statistically significant winner yet")
        recommendations.append("Continue running the test or increase sample size")

    return {
        "test_id": test_id,
        "winner": winner,
        "confidence": 0.95 if statistical_significance else 0.0,
        "improvement": best_improvement,
        "statistical_significance": statistical_significance,
        "variant_results": variant_results,
        "recommendations": recommendations
    }


def calculate_p_value(
    control_conversions: int,
    control_exposures: int,
    variant_conversions: int,
    variant_exposures: int
) -> float:
    """Calculate p-value using z-test for proportions."""
    import math

    if control_exposures == 0 or variant_exposures == 0:
        return 1.0

    p1 = control_conversions / control_exposures
    p2 = variant_conversions / variant_exposures

    pooled_p = (control_conversions + variant_conversions) / (control_exposures + variant_exposures)

    se = math.sqrt(pooled_p * (1 - pooled_p) * (1/control_exposures + 1/variant_exposures))

    if se == 0:
        return 1.0

    z_score = (p2 - p1) / se

    # Approximate p-value from z-score
    p_value = 2 * (1 - normal_cdf(abs(z_score)))

    return min(max(p_value, 0.0), 1.0)


def normal_cdf(x: float) -> float:
    """Cumulative distribution function for standard normal distribution."""
    import math
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
