"""AWS service for budget management."""

from config import Config


class AWSService:
    """Service class for AWS operations."""
    
    def __init__(self):
        self.config = Config()
    
    def create_budget(self):
        """Create an AWS budget for cost control."""
        if not self.config.CREATE_AWS_BUDGET:
            print("[AWS] Budget creation disabled")
            return
        
        try:
            import boto3
            
            # Initialize clients
            budgets_client = boto3.client("budgets", region_name=self.config.AWS_REGION)
            sts_client = boto3.client("sts")
            
            # Get account ID
            account_id = sts_client.get_caller_identity()["Account"]
            
            # Define budget
            budget_name = "LearningBudget-$5"
            budget = {
                "BudgetName": budget_name,
                "BudgetLimit": {"Amount": "5", "Unit": "USD"},
                "TimeUnit": "MONTHLY",
                "BudgetType": "COST",
            }
            
            # Set up notifications
            notifications_with_subscribers = []
            if self.config.AWS_BUDGET_EMAIL:
                notifications_with_subscribers.append({
                    "Notification": {
                        "NotificationType": "ACTUAL",
                        "ComparisonOperator": "GREATER_THAN",
                        "Threshold": 80.0,
                        "ThresholdType": "PERCENTAGE"
                    },
                    "Subscribers": [{"SubscriptionType": "EMAIL", "Address": self.config.AWS_BUDGET_EMAIL}]
                })
            
            # Create budget
            budgets_client.create_budget(
                AccountId=account_id,
                Budget=budget,
                NotificationsWithSubscribers=notifications_with_subscribers,
            )
            
            print(f"[AWS] Created budget '{budget_name}' for $5/month with email alerts.")
            
        except ImportError:
            print("[AWS] boto3 not installed. Skipping budget creation.")
        except Exception as e:
            print(f"[AWS] Error creating budget: {e}")