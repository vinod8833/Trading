from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from trading.home_view import HomeView
from trading.views import (
    StockAnalysisViewSet,
    TradeRecommendationViewSet,
    PortfolioViewSet,
    RiskAssessmentViewSet,
    SignalGenerationViewSet,
    RiskAnalysisViewSet,
    MarketSummaryViewSet,
    PortfolioHealthViewSet,
    TradingMistakeDetectorViewSet,
    AIExplainerViewSet,
    PaperTradingViewSet,
    SmartAlertViewSet,
    InvestmentPlannerViewSet,
    IntradaySignalViewSet,
    SupportResistanceViewSet,
    TechnicalAnalysisViewSet,
    DynamicStockRecommendationViewSet,
    StockScannerViewSet,
    DynamicStockAnalysisViewSet
)
from trading.user_views import UserProfileView, UserSettingsView, UserChangePasswordView
from trading.ai_engine_views import (
    FormulaCalculatorView,
    MarketAnalysisView,
    TraderTypeMapperView,
    AISignalGeneratorView,
    FormularMetadataView
)

router = DefaultRouter()
router.register(r'stocks', StockAnalysisViewSet, basename='stock')
router.register(r'recommendations', TradeRecommendationViewSet, basename='recommendation')
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'risk', RiskAssessmentViewSet, basename='risk')

router.register(r'signals', SignalGenerationViewSet, basename='signals')
router.register(r'risk-analysis', RiskAnalysisViewSet, basename='risk-analysis')
router.register(r'market-summary', MarketSummaryViewSet, basename='market-summary')
router.register(r'portfolio-health', PortfolioHealthViewSet, basename='portfolio-health')
router.register(r'mistake-detector', TradingMistakeDetectorViewSet, basename='mistake-detector')
router.register(r'ai-explain', AIExplainerViewSet, basename='ai-explain')
router.register(r'paper-trading', PaperTradingViewSet, basename='paper-trading')
router.register(r'smart-alerts', SmartAlertViewSet, basename='smart-alerts')
router.register(r'investment-planner', InvestmentPlannerViewSet, basename='investment-planner')
router.register(r'intraday-signals', IntradaySignalViewSet, basename='intraday-signals')
router.register(r'support-resistance', SupportResistanceViewSet, basename='support-resistance')
router.register(r'technical-analysis', TechnicalAnalysisViewSet, basename='technical-analysis')

router.register(r'stock-recommendations', DynamicStockRecommendationViewSet, basename='stock-recommendations')
router.register(r'stock-scanner', StockScannerViewSet, basename='stock-scanner')
router.register(r'stock-analysis', DynamicStockAnalysisViewSet, basename='stock-analysis')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', HomeView.as_view()),
    
    path('api/auth/', include('trading.auth_urls')),
    
    path('api/users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/users/settings/', UserSettingsView.as_view(), name='user-settings'),
    path('api/users/change-password/', UserChangePasswordView.as_view(), name='user-change-password'),
    
    path('api/ai/calculate-formula/', FormulaCalculatorView.as_view(), name='calculate-formula'),
    path('api/ai/market-analysis/', MarketAnalysisView.as_view(), name='market-analysis'),
    path('api/ai/trader-types/', TraderTypeMapperView.as_view(), name='trader-types'),
    path('api/ai/generate-signal/', AISignalGeneratorView.as_view(), name='generate-signal'),
    path('api/ai/formulas/', FormularMetadataView.as_view(), name='formula-metadata'),
    
    path('api/ai/', include('trading.ai_signals_urls')),
    
    path('api/', include(router.urls)),
    
    path('api/groww/', include('trading.groww_urls')),
    
    path('api/market/', include('trading.market_urls')),
    
    path('health/', include('trading.health_urls')),
]
