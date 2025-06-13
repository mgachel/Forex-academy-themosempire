from django.test import TestCase
from .models import Feature

class FeatureModelTest(TestCase):

    def setUp(self):
        Feature.objects.create(
            title="AI-Powered Learning",
            description="Our proprietary machine learning algorithms adapt to your learning style, providing personalized trading strategies and real-time market insights."
        )
        Feature.objects.create(
            title="Quantum Analytics",
            description="Leverage quantum computing principles to analyze market patterns with unprecedented accuracy and predict trends before they happen."
        )
        Feature.objects.create(
            title="Global Community",
            description="Join thousands of successful traders worldwide in our exclusive community platform with real-time collaboration and mentorship programs."
        )

    def test_feature_creation(self):
        feature = Feature.objects.get(title="AI-Powered Learning")
        self.assertEqual(feature.description, "Our proprietary machine learning algorithms adapt to your learning style, providing personalized trading strategies and real-time market insights.")

    def test_feature_count(self):
        count = Feature.objects.count()
        self.assertEqual(count, 3)