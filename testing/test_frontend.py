"""
Frontend Validation Test Suite for Food Rescue Platform
Tests file structure, configuration, component integrity, and build pipeline.

Run with:  python -m pytest testing/test_frontend.py -v --tb=short
"""
import pytest
import os
import json
import subprocess

# ── Paths ───────────────────────────────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
SRC_DIR = os.path.join(FRONTEND_DIR, 'src')
APP_DIR = os.path.join(SRC_DIR, 'app')
COMPONENTS_DIR = os.path.join(SRC_DIR, 'components')
LIB_DIR = os.path.join(SRC_DIR, 'lib')


def _exists(path: str) -> bool:
    return os.path.isfile(os.path.normpath(path))


def _read(path: str) -> str:
    with open(os.path.normpath(path), 'r', encoding='utf-8') as f:
        return f.read()


# ═══════════════════════════════════════════════════════════════════════════
# 1. PAGE FILES EXIST (6 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestPageFilesExist:
    """Verify all implemented page files are present."""

    def test_home_page(self):
        assert _exists(os.path.join(APP_DIR, 'page.tsx')), "Home page missing"

    def test_login_page(self):
        assert _exists(os.path.join(APP_DIR, 'login', 'page.tsx')), "Login page missing"

    def test_register_page(self):
        assert _exists(os.path.join(APP_DIR, 'register', 'page.tsx')), "Register page missing"

    def test_admin_dashboard(self):
        assert _exists(os.path.join(APP_DIR, 'dashboard', 'admin', 'page.tsx')), "Admin dashboard missing"

    def test_dispatcher_dashboard(self):
        assert _exists(os.path.join(APP_DIR, 'dashboard', 'dispatcher', 'page.tsx')), "Dispatcher dashboard missing"

    def test_ngo_dashboard(self):
        assert _exists(os.path.join(APP_DIR, 'dashboard', 'ngo', 'page.tsx')), "NGO dashboard missing"


# ═══════════════════════════════════════════════════════════════════════════
# 2. COMPONENT FILES EXIST (10 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestComponentFilesExist:
    """Verify all implemented component files are present."""

    @pytest.mark.parametrize("component", [
        "Navbar.tsx",
        "HeroSection.tsx",
        "FeaturesSection.tsx",
        "IntelligentDistribution.tsx",
        "EcosystemSection.tsx",
        "CTASection.tsx",
        "TrustedByMarquee.tsx",
        "Footer.tsx",
        "ParallaxBackground.tsx",
        "RevealOnScroll.tsx",
    ])
    def test_component_exists(self, component):
        assert _exists(os.path.join(COMPONENTS_DIR, component)), f"{component} missing"


# ═══════════════════════════════════════════════════════════════════════════
# 3. LIBRARY FILES EXIST (5 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestLibFilesExist:
    """Verify all implemented library modules are present."""

    @pytest.mark.parametrize("lib_file", [
        "api-config.ts",
        "api-service.ts",
        "auth-context.tsx",
        "toast-context.tsx",
        "websocket-service.ts",
    ])
    def test_lib_exists(self, lib_file):
        assert _exists(os.path.join(LIB_DIR, lib_file)), f"{lib_file} missing"


# ═══════════════════════════════════════════════════════════════════════════
# 4. PACKAGE.JSON VALIDATION (4 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestPackageJson:
    """Validate package.json contains required entries."""

    @pytest.fixture(autouse=True)
    def load_package(self):
        path = os.path.normpath(os.path.join(FRONTEND_DIR, 'package.json'))
        with open(path, 'r', encoding='utf-8') as f:
            self.pkg = json.load(f)

    def test_has_name(self):
        assert "name" in self.pkg

    def test_has_required_dependencies(self):
        deps = self.pkg.get("dependencies", {})
        for dep in ["next", "react", "react-dom"]:
            assert dep in deps, f"Missing dependency: {dep}"

    def test_has_dev_script(self):
        scripts = self.pkg.get("scripts", {})
        assert "dev" in scripts, "Missing 'dev' script"

    def test_has_build_script(self):
        scripts = self.pkg.get("scripts", {})
        assert "build" in scripts, "Missing 'build' script"


# ═══════════════════════════════════════════════════════════════════════════
# 5. TSCONFIG VALIDATION (2 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestTsConfig:
    """Validate TypeScript configuration."""

    def test_tsconfig_exists(self):
        assert _exists(os.path.join(FRONTEND_DIR, 'tsconfig.json')), "tsconfig.json missing"

    def test_tsconfig_valid_json(self):
        path = os.path.normpath(os.path.join(FRONTEND_DIR, 'tsconfig.json'))
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert "compilerOptions" in data, "compilerOptions missing from tsconfig"


# ═══════════════════════════════════════════════════════════════════════════
# 6. API CONFIG VALIDATION (3 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestApiConfig:
    """Validate api-config.ts contains all expected endpoint strings."""

    @pytest.fixture(autouse=True)
    def load_config(self):
        self.content = _read(os.path.join(LIB_DIR, 'api-config.ts'))

    def test_has_auth_endpoints(self):
        for ep in ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/me"]:
            assert ep in self.content, f"Missing endpoint: {ep}"

    def test_has_task_endpoints(self):
        for ep in ["/api/v1/tasks"]:
            assert ep in self.content, f"Missing endpoint: {ep}"

    def test_has_volunteer_endpoints(self):
        for ep in ["/api/v1/volunteers"]:
            assert ep in self.content, f"Missing endpoint: {ep}"


# ═══════════════════════════════════════════════════════════════════════════
# 7. COMPONENT STRUCTURE VALIDATION (10 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestComponentStructure:
    """Validate each component has a proper export."""

    @pytest.mark.parametrize("component", [
        "Navbar.tsx",
        "HeroSection.tsx",
        "FeaturesSection.tsx",
        "IntelligentDistribution.tsx",
        "EcosystemSection.tsx",
        "CTASection.tsx",
        "TrustedByMarquee.tsx",
        "Footer.tsx",
        "ParallaxBackground.tsx",
        "RevealOnScroll.tsx",
    ])
    def test_component_has_export(self, component):
        content = _read(os.path.join(COMPONENTS_DIR, component))
        has_export = ("export default" in content or "export function" in content)
        assert has_export, f"{component} has no export default or export function"


# ═══════════════════════════════════════════════════════════════════════════
# 8. AUTH CONTEXT VALIDATION (2 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthContext:
    """Validate auth-context.tsx exports expected symbols."""

    @pytest.fixture(autouse=True)
    def load_auth(self):
        self.content = _read(os.path.join(LIB_DIR, 'auth-context.tsx'))

    def test_exports_auth_provider(self):
        assert "AuthProvider" in self.content, "AuthProvider not found in auth-context"

    def test_exports_use_auth(self):
        assert "useAuth" in self.content, "useAuth not found in auth-context"


# ═══════════════════════════════════════════════════════════════════════════
# 9. API SERVICE VALIDATION (3 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestApiService:
    """Validate api-service.ts has core methods."""

    @pytest.fixture(autouse=True)
    def load_service(self):
        self.content = _read(os.path.join(LIB_DIR, 'api-service.ts'))

    def test_has_login_method(self):
        assert "async login(" in self.content, "login method missing"

    def test_has_register_method(self):
        assert "async register(" in self.content, "register method missing"

    def test_has_get_me_method(self):
        assert "async getMe(" in self.content, "getMe method missing"


# ═══════════════════════════════════════════════════════════════════════════
# 10. LAYOUT & GLOBAL STYLES (2 tests)
# ═══════════════════════════════════════════════════════════════════════════

class TestLayoutAndStyles:
    """Validate layout.tsx and globals.css exist."""

    def test_layout_exists(self):
        assert _exists(os.path.join(APP_DIR, 'layout.tsx')), "layout.tsx missing"

    def test_globals_css_exists(self):
        assert _exists(os.path.join(APP_DIR, 'globals.css')), "globals.css missing"


# ═══════════════════════════════════════════════════════════════════════════
# 11. NEXT.JS BUILD TEST (1 test — may take 30-60s)
# ═══════════════════════════════════════════════════════════════════════════

class TestNextBuild:
    """Verify the Next.js project builds successfully (catches TS/import errors)."""

    def test_next_build(self):
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=os.path.normpath(FRONTEND_DIR),
            capture_output=True,
            text=True,
            timeout=180,
            shell=True,
        )
        assert result.returncode == 0, (
            f"Next.js build failed (exit code {result.returncode}).\n"
            f"STDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )
