import requests
import logging
from django.conf import settings
from decimal import Decimal
from datetime import datetime
import json
import hmac
import hashlib
import base64
from abc import ABC, abstractmethod

# Set up logging
logger = logging.getLogger(__name__)

class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, amount, reference_id, customer_info):
        pass

class BkashGateway(PaymentGateway):
    def __init__(self, config):
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']
        self.username = config['username']
        self.password = config['password']
        self.sandbox_mode = config['sandbox_mode']
        self.base_url = 'https://checkout.sandbox.bka.sh/v1.2.0-beta' if self.sandbox_mode else 'https://checkout.pay.bka.sh/v1.2.0-beta'
        self._auth_token = None

    def _get_auth_token(self):
        if not self._auth_token:
            url = f"{self.base_url}/checkout/token/grant"
            headers = {
                'username': self.username,
                'password': self.password
            }
            data = {
                'app_key': self.api_key,
                'app_secret': self.api_secret
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                self._auth_token = response.json().get('id_token')
            except requests.exceptions.RequestException as e:
                raise Exception(f"Failed to get bKash auth token: {str(e)}")
        return self._auth_token

    def process_payment(self, amount, reference_id, customer_info):
        try:
            # Validate required customer info
            if not customer_info.get('number') or not customer_info.get('pin'):
                raise ValueError("bKash number and PIN are required")

            # In sandbox mode, simulate successful payment for testing
            if self.sandbox_mode:
                if customer_info['pin'] == '12345':  # Test PIN
                    return {
                        'status': 'success',
                        'transaction_id': f'TEST-{reference_id}',
                        'message': 'Payment successful (Test Mode)'
                    }
                else:
                    return {
                        'status': 'failed',
                        'message': 'Invalid PIN (Test Mode)'
                    }

            # Real bKash payment processing
            auth_token = self._get_auth_token()
            url = f"{self.base_url}/checkout/payment/create"
            headers = {
                'Authorization': auth_token,
                'X-APP-Key': self.api_key
            }
            data = {
                'amount': str(amount),
                'currency': 'BDT',
                'intent': 'sale',
                'merchantInvoiceNumber': reference_id,
                'merchantAssociationInfo': 'Hospital Management System'
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            if result.get('statusCode') == '0000':
                return {
                    'status': 'success',
                    'transaction_id': result.get('paymentID'),
                    'message': 'Payment successful'
                }
            else:
                return {
                    'status': 'failed',
                    'message': result.get('statusMessage', 'Payment failed')
                }

        except requests.exceptions.RequestException as e:
            return {
                'status': 'failed',
                'message': f'Payment processing error: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Payment failed: {str(e)}'
            }

class RocketGateway(PaymentGateway):
    def __init__(self, config):
        self.config = config

    def process_payment(self, amount, reference_id, customer_info):
        # Implement Rocket payment processing
        pass

class DBBLGateway(PaymentGateway):
    def __init__(self, config):
        self.config = config

    def process_payment(self, amount, reference_id, customer_info):
        # Implement DBBL payment processing
        pass

def get_payment_gateway(gateway_name='bkash'):
    """
    Factory function to get the appropriate payment gateway instance
    """
    gateway_configs = getattr(settings, 'PAYMENT_GATEWAYS', {})
    gateway_config = gateway_configs.get(gateway_name, {})
    
    if not gateway_config:
        raise ValueError(f"Configuration for payment gateway '{gateway_name}' not found")

    gateway_classes = {
        'bkash': BkashGateway,
        'rocket': RocketGateway,
        'dbbl': DBBLGateway
    }

    gateway_class = gateway_classes.get(gateway_name)
    if not gateway_class:
        raise ValueError(f"Payment gateway '{gateway_name}' not supported")

    return gateway_class(gateway_config) 