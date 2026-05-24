import os
import sys
import argparse
from core.di.container import container


def configure_dependencies(db_path: str = "financial_compass.db"):
    """Упрощенная настройка зависимостей"""

    print(f"🔧 Configuring DI Container with database: {db_path}")

    container.register_param('db_path', db_path)

    from infrastructure.database.sqlite_repository import (
        SQLiteUserRepository, SQLiteOperationRepository, SQLiteBudgetRepository
    )
    from infrastructure.database.sqlite_goal_repository import SQLiteGoalRepository
    from infrastructure.database.sqlite_scheduled_payment_repository import SQLiteScheduledPaymentRepository
    from infrastructure.database.sqlite_auto_category_repository import SQLiteAutoCategoryRepository
    from infrastructure.database.transaction_repository import TransactionRepository

    from core.services.user_service import UserService
    from core.services.operation_service import OperationService
    from core.services.admin_service import AdminService
    from core.services.budget_service import BudgetService
    from core.services.report_service import ReportService
    from core.services.financial_calculator import FinancialCalculator
    from core.services.backup_service import BackupService
    from core.services.goal_service import GoalService
    from core.services.scheduled_payment_service import ScheduledPaymentService
    from core.services.auto_category_service import AutoCategoryService
    from core.services.notification_service import NotificationService
    from core.services.transaction_service import TransactionService

    from core.services.visualization.pie_chart_generator import PieChartGenerator
    from core.services.visualization.bar_chart_generator import BarChartGenerator
    from core.services.visualization.budget_chart_generator import BudgetChartGenerator
    from core.services.visualization.chart_styler import DefaultChartStyler
    from core.factories.chart_factory import ChartFactory

    from infrastructure.security.simple_auth_service import SimpleAuthService

    from core.interfaces.repositories import (
        IUserRepository, IOperationRepository, IBudgetRepository,
        IGoalRepository, IScheduledPaymentRepository,
        IAutoCategoryRepository
    )
    from core.interfaces.services import (
        IUserService, IOperationService, IAdminService,
        IBudgetService, IReportService, IFinancialCalculator,
        IAuthenticationService, IGoalService, IScheduledPaymentService,
        IAutoCategoryService, INotificationService, ITransactionService
    )
    from core.interfaces.visualization import (
        IPieChartGenerator, IBarChartGenerator, IBudgetChartGenerator, IChartStyler
    )

    user_repo = SQLiteUserRepository(db_path)
    operation_repo = SQLiteOperationRepository(db_path)
    budget_repo = SQLiteBudgetRepository(db_path)
    goal_repo = SQLiteGoalRepository(db_path)
    payment_repo = SQLiteScheduledPaymentRepository(db_path)
    auth_service = SimpleAuthService()
    chart_styler = DefaultChartStyler()
    auto_category_repo = SQLiteAutoCategoryRepository(db_path)
    transaction_repo = TransactionRepository(db_path)

    user_service = UserService(user_repo, auth_service)
    operation_service = OperationService(operation_repo)
    admin_service = AdminService(user_repo, operation_repo)
    calculator = FinancialCalculator(operation_repo, user_repo)
    budget_service = BudgetService(budget_repo, calculator)
    report_service = ReportService(operation_repo)
    backup_service = BackupService(db_path)
    goal_service = GoalService(goal_repo, operation_repo)
    payment_service = ScheduledPaymentService(payment_repo, operation_repo)
    auto_category_service = AutoCategoryService(auto_category_repo)
    notification_service = NotificationService(operation_repo, budget_repo, goal_service, payment_repo)
    transaction_service = TransactionService(transaction_repo)

    pie_generator = PieChartGenerator()
    bar_generator = BarChartGenerator()
    budget_generator = BudgetChartGenerator()
    chart_factory = ChartFactory(chart_styler)

    container.register_instance(IUserRepository, user_repo)
    container.register_instance(IOperationRepository, operation_repo)
    container.register_instance(IBudgetRepository, budget_repo)
    container.register_instance(IGoalRepository, goal_repo)
    container.register_instance(IScheduledPaymentRepository, payment_repo)
    container.register_instance(IAuthenticationService, auth_service)
    container.register_instance(IUserService, user_service)
    container.register_instance(IOperationService, operation_service)
    container.register_instance(IAdminService, admin_service)
    container.register_instance(IBudgetService, budget_service)
    container.register_instance(IReportService, report_service)
    container.register_instance(IFinancialCalculator, calculator)
    container.register_instance(IGoalService, goal_service)
    container.register_instance(IScheduledPaymentService, payment_service)
    container.register_instance(IPieChartGenerator, pie_generator)
    container.register_instance(IBarChartGenerator, bar_generator)
    container.register_instance(IBudgetChartGenerator, budget_generator)
    container.register_instance(IChartStyler, chart_styler)
    container.register_instance(ChartFactory, chart_factory)
    container.register_instance(IAutoCategoryRepository, auto_category_repo)
    container.register_instance(IAutoCategoryService, auto_category_service)
    container.register_instance(INotificationService, notification_service)
    container.register_instance(ITransactionService, transaction_service)

    from application.commands.command_registry import command_registry
    from application.commands.user_commands import (
        UserCommandHandler, RegisterUserCommand, LoginUserCommand, CreateAdminCommand
    )
    from application.commands.admin_commands import (
        AdminCommandHandler, DeactivateUserCommand, ActivateUserCommand, GetSystemStatsCommand
    )
    from application.commands.budget_commands import (
        BudgetCommandHandler, SetBudgetLimitCommand, GetBudgetLimitsCommand,
        CheckBudgetStatusCommand, DeleteBudgetLimitCommand
    )
    from application.commands.operation_commands import (
        OperationCommandHandler, DeleteOperationCommand, UpdateOperationCommand
    )
    from application.commands.report_commands import (
        ReportCommandHandler, GenerateCategoryReportCommand,
        GenerateTrendReportCommand, GenerateBudgetReportCommand
    )
    from application.commands.backup_commands import (
        BackupCommandHandler, ExportToSQLiteCommand, ExportToJSONCommand,
        ImportFromSQLiteCommand, ImportFromJSONCommand
    )

    command_registry.register(RegisterUserCommand, UserCommandHandler)
    command_registry.register(LoginUserCommand, UserCommandHandler)
    command_registry.register(CreateAdminCommand, UserCommandHandler)
    command_registry.register(DeactivateUserCommand, AdminCommandHandler)
    command_registry.register(ActivateUserCommand, AdminCommandHandler)
    command_registry.register(GetSystemStatsCommand, AdminCommandHandler)
    command_registry.register(SetBudgetLimitCommand, BudgetCommandHandler)
    command_registry.register(GetBudgetLimitsCommand, BudgetCommandHandler)
    command_registry.register(CheckBudgetStatusCommand, BudgetCommandHandler)
    command_registry.register(DeleteBudgetLimitCommand, BudgetCommandHandler)
    command_registry.register(DeleteOperationCommand, OperationCommandHandler)
    command_registry.register(UpdateOperationCommand, OperationCommandHandler)
    command_registry.register(GenerateCategoryReportCommand, ReportCommandHandler)
    command_registry.register(GenerateTrendReportCommand, ReportCommandHandler)
    command_registry.register(GenerateBudgetReportCommand, ReportCommandHandler)
    command_registry.register(ExportToSQLiteCommand, BackupCommandHandler)
    command_registry.register(ExportToJSONCommand, BackupCommandHandler)
    command_registry.register(ImportFromSQLiteCommand, BackupCommandHandler)
    command_registry.register(ImportFromJSONCommand, BackupCommandHandler)

    print("✅ DI Container configured successfully!")

    return {
        'user_service': user_service,
        'operation_service': operation_service,
        'admin_service': admin_service,
        'budget_service': budget_service,
        'report_service': report_service,
        'backup_service': backup_service,
        'goal_service': goal_service,
        'payment_service': payment_service,
        'financial_calculator': calculator,
        'user_repository': user_repo,
        'operation_repository': operation_repo,
        'budget_repository': budget_repo,
        'goal_repository': goal_repo,
        'payment_repository': payment_repo,
        'pie_generator': pie_generator,
        'bar_generator': bar_generator,
        'budget_generator': budget_generator,
        'chart_factory': chart_factory,
        'auto_category_repository': auto_category_repo,
        'auto_category_service': auto_category_service,
        'notification_service': notification_service,
        'transaction_repository': transaction_repo,
        'transaction_service': transaction_service,
    }


class FinancialCompassApp:
    def __init__(self, db_path: str = "financial_compass.db"):
        print(f"🚀 Initializing Financial Compass Application")

        os.makedirs("reports", exist_ok=True)
        os.makedirs("backups", exist_ok=True)

        self.services = configure_dependencies(db_path)
        self._initialize_command_handlers()

        print("✅ Application initialized successfully!")

    def _initialize_command_handlers(self):
        user_service = self.services['user_service']
        operation_service = self.services['operation_service']
        admin_service = self.services['admin_service']
        budget_service = self.services['budget_service']
        report_service = self.services['report_service']
        backup_service = self.services['backup_service']
        goal_service = self.services['goal_service']
        payment_service = self.services['payment_service']
        financial_calculator = self.services['financial_calculator']
        user_repository = self.services['user_repository']
        chart_factory = self.services['chart_factory']
        pie_generator = self.services['pie_generator']
        auto_category_service = self.services['auto_category_service']
        notification_service = self.services['notification_service']
        transaction_service = self.services['transaction_service']

        from application.commands.user_commands import UserCommandHandler
        from application.commands.admin_commands import AdminCommandHandler
        from application.commands.budget_commands import BudgetCommandHandler
        from application.commands.operation_commands import OperationCommandHandler
        from application.commands.report_commands import ReportCommandHandler
        from application.commands.backup_commands import BackupCommandHandler

        self.user_command_handler = UserCommandHandler(user_service)
        self.admin_command_handler = AdminCommandHandler(admin_service, user_repository)
        self.budget_command_handler = BudgetCommandHandler(budget_service, chart_factory)
        self.operation_command_handler = OperationCommandHandler(operation_service)
        self.report_command_handler = ReportCommandHandler(report_service, pie_generator)
        self.backup_command_handler = BackupCommandHandler(backup_service)

        self.user_service = user_service
        self.operation_service = operation_service
        self.admin_service = admin_service
        self.budget_service = budget_service
        self.report_service = report_service
        self.backup_service = backup_service
        self.goal_service = goal_service
        self.payment_service = payment_service
        self.financial_calculator = financial_calculator
        self.notification_service = notification_service
        self.auto_category_service = auto_category_service
        self.transaction_service = transaction_service

        self.user_repository = user_repository
        self.operation_repository = self.services['operation_repository']
        self.budget_repository = self.services['budget_repository']
        self.goal_repository = self.services['goal_repository']
        self.payment_repository = self.services['payment_repository']
        self.transaction_repository = self.services['transaction_repository']

        self.visualization_service = pie_generator

        print("✅ Command handlers initialized:")
        print(f"   - user_command_handler: {self.user_command_handler}")
        print(f"   - admin_command_handler: {self.admin_command_handler}")
        print(f"   - budget_command_handler: {self.budget_command_handler}")
        print(f"   - operation_command_handler: {self.operation_command_handler}")
        print(f"   - report_command_handler: {self.report_command_handler}")
        print(f"   - backup_command_handler: {self.backup_command_handler}")
        print(f"   - transaction_service: {self.transaction_service}")
        print(f"   - goal_service: {self.goal_service}")

    def run(self):
        try:
            self._check_gui_dependencies()
            self._run_gui()
        except ImportError as e:
            print(f"❌ GUI dependencies missing: {e}")
            print("📦 Please install: pip install matplotlib")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _check_gui_dependencies(self):
        try:
            import tkinter
            import matplotlib
            print("✅ GUI dependencies check passed")
        except ImportError as e:
            raise ImportError(f"Missing GUI dependency: {e}")

    def _run_gui(self):
        from presentation.gui.main_window import FinancialCompassGUI
        print("🖥️  Starting GUI...")
        gui = FinancialCompassGUI(self)
        gui.run()


def check_gui_dependencies():
    missing_deps = []
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    if missing_deps:
        print("⚠️  Warning: Missing GUI dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n📦 Install dependencies with:")
        print("   pip install matplotlib")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description='💰 Financial Compass - Personal Finance Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Run with default database
  python main.py --db my_finances.db # Run with custom database
        """
    )
    parser.add_argument('--db', type=str, default='financial_compass.db', help='Path to database file (default: financial_compass.db)')
    parser.add_argument('--version', action='version', version='Financial Compass v1.0.0')
    args = parser.parse_args()

    print("=" * 50)
    print("💰 FINANCIAL COMPASS v1.0.0")
    print("=" * 50)

    if not check_gui_dependencies():
        print("\n❌ Cannot start GUI without dependencies.")
        print("   Please install missing packages and try again.")
        sys.exit(1)

    try:
        print(f"📁 Database: {args.db}")
        print("🔄 Initializing application...")
        app = FinancialCompassApp(args.db)
        app.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical error during startup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()