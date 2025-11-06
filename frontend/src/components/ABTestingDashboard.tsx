/**
 * A/B Testing Dashboard
 *
 * Management interface for A/B tests:
 * - View all tests
 * - Create new tests
 * - Monitor results in real-time
 * - Statistical analysis
 * - Winner declaration
 */
import React, { useState, useEffect } from 'react';
import {
  TrendingUp, Play, Pause, StopCircle, Plus, Edit,
  Trash2, Users, Target, Award, AlertCircle, Check,
  ChevronRight, BarChart3, PieChart, Activity
} from 'lucide-react';
import { ABTest, TestResults, Variant, abTestingService } from '../services/ABTestingService';

const ABTestingDashboard: React.FC = () => {
  const [tests, setTests] = useState<ABTest[]>([]);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    const response = await fetch('/api/v1/ab-testing/tests');
    const data = await response.json();
    setTests(data);
  };

  const filteredTests = tests.filter((test) => {
    if (filter === 'all') return true;
    return test.status === filter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">A/B Testing</h1>
          <p className="text-gray-600">Optimize user experience with data-driven experiments</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium shadow-md"
        >
          <Plus className="w-5 h-5" />
          <span>Create Test</span>
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Activity className="w-6 h-6" />}
          label="Active Tests"
          value={tests.filter((t) => t.status === 'active').length}
          color="from-blue-500 to-blue-600"
        />
        <StatCard
          icon={<Users className="w-6 h-6" />}
          label="Total Exposures"
          value={tests.reduce(
            (sum, t) => sum + t.variants.reduce((s, v) => s + v.exposures, 0),
            0
          ).toLocaleString()}
          color="from-purple-500 to-purple-600"
        />
        <StatCard
          icon={<Target className="w-6 h-6" />}
          label="Conversions"
          value={tests.reduce(
            (sum, t) => sum + t.variants.reduce((s, v) => s + v.conversions, 0),
            0
          ).toLocaleString()}
          color="from-green-500 to-green-600"
        />
        <StatCard
          icon={<Award className="w-6 h-6" />}
          label="Completed Tests"
          value={tests.filter((t) => t.status === 'completed').length}
          color="from-indigo-500 to-indigo-600"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-2 mb-6">
        {[
          { value: 'all' as const, label: 'All Tests' },
          { value: 'active' as const, label: 'Active' },
          { value: 'completed' as const, label: 'Completed' },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setFilter(tab.value)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === tab.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tests List */}
      <div className="space-y-4">
        {filteredTests.map((test) => (
          <TestCard
            key={test.id}
            test={test}
            onSelect={() => setSelectedTest(test)}
            onRefresh={loadTests}
          />
        ))}

        {filteredTests.length === 0 && (
          <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">No tests found</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Create your first A/B test
            </button>
          </div>
        )}
      </div>

      {/* Test Detail Modal */}
      {selectedTest && (
        <TestDetailModal
          test={selectedTest}
          onClose={() => setSelectedTest(null)}
          onRefresh={loadTests}
        />
      )}

      {/* Create Test Modal */}
      {showCreateModal && (
        <CreateTestModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            loadTests();
          }}
        />
      )}
    </div>
  );
};

/**
 * Stat Card Component
 */
const StatCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
}> = ({ icon, label, value, color }) => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center text-white mb-4`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
};

/**
 * Test Card Component
 */
const TestCard: React.FC<{
  test: ABTest;
  onSelect: () => void;
  onRefresh: () => void;
}> = ({ test, onSelect, onRefresh }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'completed':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'paused':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const handleStart = async () => {
    await abTestingService.startTest(test.id);
    onRefresh();
  };

  const handleStop = async () => {
    await abTestingService.stopTest(test.id);
    onRefresh();
  };

  const totalExposures = test.variants.reduce((sum, v) => sum + v.exposures, 0);
  const totalConversions = test.variants.reduce((sum, v) => sum + v.conversions, 0);
  const overallConversionRate = totalExposures > 0 ? (totalConversions / totalExposures) * 100 : 0;

  return (
    <div className="bg-white border-2 border-gray-200 rounded-xl shadow-md p-6 hover:border-indigo-300 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-xl font-bold text-gray-900">{test.name}</h3>
            <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${getStatusColor(test.status)}`}>
              {test.status.toUpperCase()}
            </span>
          </div>
          <p className="text-gray-600 mb-4">{test.description}</p>

          {/* Variants Summary */}
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center text-gray-600">
              <Users className="w-4 h-4 mr-2" />
              <span>{test.variants.length} variants</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Activity className="w-4 h-4 mr-2" />
              <span>{totalExposures.toLocaleString()} exposures</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Target className="w-4 h-4 mr-2" />
              <span>{overallConversionRate.toFixed(2)}% conversion</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {test.status === 'draft' && (
            <button
              onClick={handleStart}
              className="p-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition-colors"
              title="Start test"
            >
              <Play className="w-5 h-5" />
            </button>
          )}
          {test.status === 'active' && (
            <button
              onClick={handleStop}
              className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
              title="Stop test"
            >
              <StopCircle className="w-5 h-5" />
            </button>
          )}
          <button
            onClick={onSelect}
            className="p-2 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition-colors"
            title="View details"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Variants Progress Bars */}
      <div className="space-y-2">
        {test.variants.map((variant) => (
          <div key={variant.id} className="flex items-center space-x-3">
            <div className="w-24 text-sm font-medium text-gray-700">
              {variant.name}
              {variant.isControl && (
                <span className="ml-1 text-xs text-gray-500">(Control)</span>
              )}
            </div>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-300"
                style={{
                  width: totalExposures > 0 ? `${(variant.exposures / totalExposures) * 100}%` : '0%',
                }}
              />
            </div>
            <div className="w-32 text-sm text-gray-600 text-right">
              {variant.exposures.toLocaleString()} ({variant.conversionRate.toFixed(2)}%)
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Test Detail Modal
 */
const TestDetailModal: React.FC<{
  test: ABTest;
  onClose: () => void;
  onRefresh: () => void;
}> = ({ test, onClose, onRefresh }) => {
  const [results, setResults] = useState<TestResults | null>(null);

  useEffect(() => {
    loadResults();
  }, [test.id]);

  const loadResults = async () => {
    const data = await abTestingService.getTestResults(test.id);
    setResults(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">{test.name}</h2>
              <p className="text-indigo-100">{test.description}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Results Summary */}
          {results && results.statisticalSignificance && (
            <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6 mb-6">
              <div className="flex items-center space-x-3 mb-4">
                <Award className="w-8 h-8 text-green-600" />
                <div>
                  <h3 className="text-xl font-bold text-green-900">Winner Found!</h3>
                  <p className="text-green-700">Statistically significant result achieved</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Winning Variant</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {test.variants.find((v) => v.id === results.winner)?.name}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Improvement</div>
                  <div className="text-2xl font-bold text-green-600">
                    +{results.improvement.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Confidence</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(results.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Variants Comparison */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Variant Performance</h3>
            <div className="space-y-4">
              {test.variants.map((variant) => (
                <div
                  key={variant.id}
                  className={`border-2 rounded-xl p-4 ${
                    variant.id === results?.winner
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-bold text-gray-900">{variant.name}</h4>
                      {variant.isControl && (
                        <span className="px-2 py-1 bg-gray-200 text-gray-700 text-xs font-semibold rounded-full">
                          CONTROL
                        </span>
                      )}
                      {variant.id === results?.winner && (
                        <span className="px-2 py-1 bg-green-200 text-green-700 text-xs font-semibold rounded-full flex items-center">
                          <Award className="w-3 h-3 mr-1" />
                          WINNER
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600">
                      {variant.trafficPercentage}% traffic
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4">
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Exposures</div>
                      <div className="text-xl font-bold text-gray-900">
                        {variant.exposures.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Conversions</div>
                      <div className="text-xl font-bold text-gray-900">
                        {variant.conversions.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Conv. Rate</div>
                      <div className="text-xl font-bold text-indigo-600">
                        {(variant.conversionRate * 100).toFixed(2)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600 mb-1">vs Control</div>
                      <div className={`text-xl font-bold ${
                        variant.isControl ? 'text-gray-400' : 'text-green-600'
                      }`}>
                        {variant.isControl ? '—' : `+${((variant.conversionRate / test.variants.find(v => v.isControl)!.conversionRate - 1) * 100).toFixed(1)}%`}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {results && results.recommendations.length > 0 && (
            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                Recommendations
              </h3>
              <ul className="space-y-2">
                {results.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-blue-900">
                    <Check className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Create Test Modal (Simplified)
 */
const CreateTestModal: React.FC<{
  onClose: () => void;
  onCreated: () => void;
}> = ({ onClose, onCreated }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New A/B Test</h2>
        <p className="text-gray-600 mb-4">
          Full test creation wizard would go here with forms for:
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-700 mb-6">
          <li>Test name and description</li>
          <li>Target audience selection</li>
          <li>Variant configuration</li>
          <li>Traffic split</li>
          <li>Success metrics</li>
          <li>Duration and sample size</li>
        </ul>
        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            onClick={onCreated}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Create Test
          </button>
        </div>
      </div>
    </div>
  );
};

export default ABTestingDashboard;
