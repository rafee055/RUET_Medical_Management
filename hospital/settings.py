# Payment Gateway Settings
BKASH_API_KEY = 'your_actual_bkash_api_key'
BKASH_API_SECRET = 'your_actual_bkash_api_secret'
ROCKET_API_KEY = 'your_rocket_api_key'
ROCKET_API_SECRET = 'your_rocket_api_secret'
DBBL_API_KEY = 'your_dbbl_api_key'
DBBL_API_SECRET = 'your_dbbl_api_secret'
VISA_API_KEY = 'your_visa_api_key'
VISA_API_SECRET = 'your_visa_api_secret'

# Base URL for payment callbacks
BASE_URL = 'https://your-actual-domain.com'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'payment.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'payment_gateways': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY' 