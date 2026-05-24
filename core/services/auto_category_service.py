from typing import List, Optional
from core.entities.auto_category import AutoCategoryRule
from core.interfaces.repositories import IAutoCategoryRepository
from core.interfaces.services import IAutoCategoryService


class AutoCategoryService(IAutoCategoryService):
    def __init__(self, auto_category_repository: IAutoCategoryRepository):
        self._repository = auto_category_repository

    def get_category_for_counterparty(self, user_id: int, counterparty: str) -> Optional[str]:
        rule = self._repository.find_by_user_and_counterparty(user_id, counterparty)
        if rule:
            self._repository.increment_use_count(rule.id)
            return rule.category
        return None

    def save_rule(self, user_id: int, counterparty: str, category: str) -> AutoCategoryRule:
        existing = self._repository.find_by_user_and_counterparty(user_id, counterparty)
        if existing:
            existing.category = category
            return self._repository.save(existing)

        rule = AutoCategoryRule.create(user_id, counterparty, category)
        return self._repository.save(rule)

    def update_rule(self, rule_id: int, category: str) -> AutoCategoryRule:
        rule = self._repository.find_by_id(rule_id) if hasattr(self._repository, 'find_by_id') else None
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")
        rule.category = category
        return self._repository.save(rule)

    def delete_rule(self, rule_id: int) -> bool:
        return self._repository.delete(rule_id)

    def get_all_rules(self, user_id: int) -> List[AutoCategoryRule]:
        return self._repository.find_by_user(user_id)