"""
Machine Learning Manuscript Classification

Uses ML to automatically classify manuscripts, predict outcomes,
and provide intelligent recommendations.
"""
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class ManuscriptClassifier:
    """
    ML-based manuscript classification system.

    Capabilities:
    - Automatic subject area classification
    - Article type prediction
    - Quality assessment
    - Acceptance probability prediction
    - Similar manuscript identification
    """

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)

        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2
        )

        self.subject_classifier = None
        self.quality_classifier = None
        self.acceptance_predictor = None

    def train_subject_classifier(self, db_session) -> Dict:
        """
        Train classifier for automatic subject area classification.

        Uses published manuscripts with known specializations.
        """
        from db.models import Manuscript, ManuscriptStatus

        # Get training data
        manuscripts = db_session.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.PUBLISHED,
            Manuscript.specialization_id.isnot(None),
            Manuscript.abstract.isnot(None)
        ).all()

        if len(manuscripts) < 50:
            return {
                'success': False,
                'message': 'Insufficient training data (minimum 50 manuscripts required)'
            }

        # Prepare data
        texts = [f"{m.title} {m.abstract}" for m in manuscripts]
        labels = [m.specialization_id for m in manuscripts]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )

        # Vectorize
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Train classifier
        self.subject_classifier = MultinomialNB()
        self.subject_classifier.fit(X_train_vec, y_train)

        # Evaluate
        y_pred = self.subject_classifier.predict(X_test_vec)
        accuracy = (y_pred == y_test).sum() / len(y_test)

        # Save model
        self._save_model('subject_classifier', self.subject_classifier)
        self._save_model('vectorizer', self.vectorizer)

        logger.info(f"Subject classifier trained with {accuracy:.2%} accuracy")

        return {
            'success': True,
            'accuracy': accuracy,
            'training_samples': len(manuscripts),
            'test_samples': len(y_test)
        }

    def predict_subject(self, title: str, abstract: str) -> Dict:
        """
        Predict subject area for a manuscript.

        Args:
            title: Manuscript title
            abstract: Manuscript abstract

        Returns:
            Dictionary with prediction and confidence
        """
        if not self.subject_classifier:
            self._load_model('subject_classifier')

        if not self.subject_classifier:
            return {
                'error': 'Subject classifier not trained. Train the model first.'
            }

        # Vectorize text
        text = f"{title} {abstract}"
        text_vec = self.vectorizer.transform([text])

        # Predict
        prediction = self.subject_classifier.predict(text_vec)[0]
        probabilities = self.subject_classifier.predict_proba(text_vec)[0]

        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_predictions = [
            {
                'specialization_id': self.subject_classifier.classes_[i],
                'confidence': float(probabilities[i])
            }
            for i in top_indices
        ]

        return {
            'predicted_specialization_id': int(prediction),
            'confidence': float(probabilities[prediction]),
            'top_predictions': top_predictions
        }

    def train_acceptance_predictor(self, db_session) -> Dict:
        """
        Train model to predict acceptance probability.

        Features:
        - Author reputation (past acceptance rate)
        - Manuscript quality indicators
        - Reviewer recommendations
        - Historical patterns
        """
        from db.models import Manuscript, Review, ManuscriptStatus, ReviewRecommendation

        # Get manuscripts with decisions
        manuscripts = db_session.query(Manuscript).filter(
            Manuscript.status.in_([
                ManuscriptStatus.ACCEPTED,
                ManuscriptStatus.PUBLISHED,
                ManuscriptStatus.REJECTED
            ])
        ).all()

        if len(manuscripts) < 100:
            return {
                'success': False,
                'message': 'Insufficient training data (minimum 100 decided manuscripts required)'
            }

        # Extract features
        features = []
        labels = []

        for manuscript in manuscripts:
            feature_vector = self._extract_features(manuscript, db_session)
            if feature_vector:
                features.append(feature_vector)
                # Label: 1 for accepted/published, 0 for rejected
                label = 1 if manuscript.status in [ManuscriptStatus.ACCEPTED, ManuscriptStatus.PUBLISHED] else 0
                labels.append(label)

        if len(features) < 100:
            return {
                'success': False,
                'message': 'Insufficient feature data extracted'
            }

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )

        # Train Random Forest classifier
        self.acceptance_predictor = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.acceptance_predictor.fit(X_train, y_train)

        # Evaluate
        y_pred = self.acceptance_predictor.predict(X_test)
        accuracy = (y_pred == y_test).sum() / len(y_test)

        # Save model
        self._save_model('acceptance_predictor', self.acceptance_predictor)

        logger.info(f"Acceptance predictor trained with {accuracy:.2%} accuracy")

        return {
            'success': True,
            'accuracy': accuracy,
            'training_samples': len(features),
            'test_samples': len(y_test)
        }

    def predict_acceptance(self, manuscript_id: int, db_session) -> Dict:
        """
        Predict acceptance probability for a manuscript.

        Args:
            manuscript_id: Manuscript database ID
            db_session: Database session

        Returns:
            Prediction with probability and explanation
        """
        from db.models import Manuscript

        if not self.acceptance_predictor:
            self._load_model('acceptance_predictor')

        if not self.acceptance_predictor:
            return {
                'error': 'Acceptance predictor not trained. Train the model first.'
            }

        manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

        if not manuscript:
            return {'error': 'Manuscript not found'}

        # Extract features
        features = self._extract_features(manuscript, db_session)

        if not features:
            return {'error': 'Could not extract features for prediction'}

        # Predict
        prediction = self.acceptance_predictor.predict([features])[0]
        probabilities = self.acceptance_predictor.predict_proba([features])[0]

        acceptance_probability = float(probabilities[1])

        # Generate explanation
        explanation = self._generate_prediction_explanation(
            manuscript,
            features,
            acceptance_probability
        )

        return {
            'manuscript_id': manuscript.manuscript_id,
            'acceptance_probability': acceptance_probability,
            'predicted_outcome': 'Accept' if prediction == 1 else 'Reject',
            'confidence_level': 'High' if max(probabilities) > 0.75 else 'Medium' if max(probabilities) > 0.60 else 'Low',
            'explanation': explanation
        }

    def _extract_features(self, manuscript, db_session) -> Optional[List[float]]:
        """Extract feature vector from manuscript."""
        from db.models import Review, ReviewRecommendation

        try:
            features = []

            # Text features (length, readability proxies)
            features.append(len(manuscript.title.split()))  # Title length
            features.append(len(manuscript.abstract.split()))  # Abstract length
            features.append(len(manuscript.keywords) if manuscript.keywords else 0)  # Keyword count

            # Author features
            features.append(len(manuscript.authors))  # Number of authors

            # Calculate author reputation (simplified)
            author_acceptance_rate = self._calculate_author_reputation(
                manuscript.authors[0].id if manuscript.authors else None,
                db_session
            )
            features.append(author_acceptance_rate)

            # Review features
            reviews = manuscript.reviews
            if reviews:
                completed_reviews = [r for r in reviews if r.recommendation]

                if completed_reviews:
                    # Average scores
                    avg_originality = np.mean([r.score_originality for r in completed_reviews if r.score_originality])
                    avg_methodology = np.mean([r.score_methodology for r in completed_reviews if r.score_methodology])
                    avg_significance = np.mean([r.score_significance for r in completed_reviews if r.score_significance])
                    avg_clarity = np.mean([r.score_clarity for r in completed_reviews if r.score_clarity])

                    features.extend([
                        avg_originality if not np.isnan(avg_originality) else 3.0,
                        avg_methodology if not np.isnan(avg_methodology) else 3.0,
                        avg_significance if not np.isnan(avg_significance) else 3.0,
                        avg_clarity if not np.isnan(avg_clarity) else 3.0
                    ])

                    # Recommendation distribution
                    accept_count = sum(1 for r in completed_reviews if r.recommendation == ReviewRecommendation.ACCEPT)
                    minor_rev_count = sum(1 for r in completed_reviews if r.recommendation == ReviewRecommendation.MINOR_REVISIONS)

                    features.append(accept_count / len(completed_reviews))
                    features.append(minor_rev_count / len(completed_reviews))
                else:
                    # No completed reviews - use neutral values
                    features.extend([3.0, 3.0, 3.0, 3.0, 0.0, 0.0])
            else:
                # No reviews - use neutral values
                features.extend([3.0, 3.0, 3.0, 3.0, 0.0, 0.0])

            return features

        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return None

    def _calculate_author_reputation(self, author_id: Optional[int], db_session) -> float:
        """Calculate author's historical acceptance rate."""
        if not author_id:
            return 0.5  # Neutral

        from db.models import Manuscript, manuscript_authors, ManuscriptStatus

        # Get author's past manuscripts
        past_manuscripts = db_session.query(Manuscript).join(
            manuscript_authors,
            Manuscript.id == manuscript_authors.c.manuscript_id
        ).filter(
            manuscript_authors.c.author_id == author_id,
            Manuscript.status.in_([
                ManuscriptStatus.ACCEPTED,
                ManuscriptStatus.PUBLISHED,
                ManuscriptStatus.REJECTED
            ])
        ).all()

        if not past_manuscripts:
            return 0.5  # Neutral for new authors

        accepted = sum(
            1 for m in past_manuscripts
            if m.status in [ManuscriptStatus.ACCEPTED, ManuscriptStatus.PUBLISHED]
        )

        return accepted / len(past_manuscripts)

    def _generate_prediction_explanation(
        self,
        manuscript,
        features: List[float],
        acceptance_probability: float
    ) -> str:
        """Generate human-readable explanation for prediction."""
        explanations = []

        if acceptance_probability > 0.7:
            explanations.append("Strong indicators of quality")
        elif acceptance_probability > 0.5:
            explanations.append("Moderate acceptance indicators")
        else:
            explanations.append("Some concerns identified")

        # Analyze features
        if features[1] > 200:  # Abstract length
            explanations.append("comprehensive abstract")

        if features[4] > 0.7:  # Author reputation
            explanations.append("strong author track record")

        if len(manuscript.reviews) > 2:
            explanations.append("sufficient peer review")

        return " • ".join(explanations)

    def _save_model(self, name: str, model):
        """Save trained model to disk."""
        model_path = self.model_dir / f"{name}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Saved model: {name}")

    def _load_model(self, name: str):
        """Load trained model from disk."""
        model_path = self.model_dir / f"{name}.pkl"

        if not model_path.exists():
            return None

        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            if name == 'subject_classifier':
                self.subject_classifier = model
            elif name == 'acceptance_predictor':
                self.acceptance_predictor = model
            elif name == 'vectorizer':
                self.vectorizer = model

            logger.info(f"Loaded model: {name}")
            return model

        except Exception as e:
            logger.error(f"Error loading model {name}: {str(e)}")
            return None


def get_ml_recommendations(manuscript_id: int, db_session) -> Dict:
    """
    Get comprehensive ML-based recommendations for a manuscript.

    Args:
        manuscript_id: Manuscript database ID
        db_session: Database session

    Returns:
        Dictionary with classifications and predictions
    """
    from db.models import Manuscript

    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        return {'error': 'Manuscript not found'}

    classifier = ManuscriptClassifier()

    recommendations = {
        'manuscript_id': manuscript.manuscript_id,
        'title': manuscript.title
    }

    # Subject classification
    if manuscript.title and manuscript.abstract:
        subject_pred = classifier.predict_subject(manuscript.title, manuscript.abstract)
        recommendations['subject_classification'] = subject_pred

    # Acceptance prediction
    acceptance_pred = classifier.predict_acceptance(manuscript_id, db_session)
    recommendations['acceptance_prediction'] = acceptance_pred

    return recommendations
