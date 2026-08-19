import ast
import unittest
from pathlib import Path

from app.dashboard.state import DashboardState


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = PROJECT_ROOT / "src" / "app" / "dashboard"


class DashboardStateTests(unittest.TestCase):
    def test_category_navigation_is_stored_in_state(self):
        state = DashboardState()
        category = {"key": "bank", "name": "Banque"}

        state.open_category(category)

        self.assertTrue(state.showing_detail)
        self.assertEqual(state.selected_category, category)

        state.show_dashboard()

        self.assertFalse(state.showing_detail)
        self.assertIsNone(state.selected_category)

    def test_state_has_no_flet_dependency(self):
        tree = ast.parse((DASHBOARD_ROOT / "state.py").read_text(encoding="utf-8"))
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported_modules.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )

        self.assertNotIn("flet", imported_modules)


class DashboardComponentBoundaryTests(unittest.TestCase):
    def test_components_do_not_access_business_layers(self):
        forbidden_prefixes = (
            "repositories",
            "services",
            "core.events",
        )

        for path in (DASHBOARD_ROOT / "components").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported_modules = [
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            ]
            imported_modules.extend(
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            )

            for module in imported_modules:
                self.assertFalse(
                    module.startswith(forbidden_prefixes),
                    f"{path.name} dépend encore de {module}",
                )


if __name__ == "__main__":
    unittest.main()
