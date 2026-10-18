from __future__ import annotations

import dataclasses
import enum
import inspect
import json
import math
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
ENGINEERING_DIR = BACKEND_DIR.parent
PROJECT_DIR = ENGINEERING_DIR.parent
FRONTEND_DIR = ENGINEERING_DIR / "Frontend"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# ============================================================
# ENGINEERING IMPORTS
# ============================================================

from Engineering.calculation_service import build_panel_calculation
from Engineering.materials_library import available_materials
from Engineering.profiles import available_profiles

try:
    from Engineering.profiles import evergrip_profile_catalog
except ImportError:
    evergrip_profile_catalog = None


# ============================================================
# JSON SERIALISATION
# ============================================================

def json_safe(value: Any) -> Any:

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):

        if isinstance(value, float) and not math.isfinite(value):
            return None

        return value

    if isinstance(value, enum.Enum):
        return json_safe(value.value)

    if dataclasses.is_dataclass(value):

        result = {}

        for field in dataclasses.fields(value):

            try:
                result[field.name] = json_safe(
                    getattr(value, field.name)
                )
            except Exception:
                result[field.name] = None

        return result

    if isinstance(value, dict):

        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):

        return [
            json_safe(item)
            for item in value
        ]

    if hasattr(value, "item") and callable(value.item):

        try:
            return json_safe(value.item())
        except Exception:
            pass

    if inspect.isfunction(value) or inspect.isclass(value):
        return getattr(value, "__name__", str(value))

    if hasattr(value, "__dict__"):

        result = {}

        for key, item in vars(value).items():

            try:
                result[key] = json_safe(item)
            except Exception:
                result[key] = str(item)

        return result

    return str(value)


# ============================================================
# MATERIAL SERIALISATION
# ============================================================

def material_to_dict(key: str, record: Any) -> dict:

    material = getattr(record, "material", None)

    return {
        "key": key,
        "name": getattr(material, "name", key),

        "manufacturer": getattr(
            record,
            "manufacturer",
            None,
        ),

        "product": getattr(
            record,
            "product",
            None,
        ),

        "standard_grade": getattr(
            record,
            "standard_grade",
            None,
        ),

        "youngs_modulus": getattr(
            material,
            "youngs_modulus",
            None,
        ),

        "transverse_youngs_modulus": getattr(
            material,
            "transverse_youngs_modulus",
            None,
        ),

        "shear_modulus": getattr(
            material,
            "shear_modulus",
            None,
        ),

        "allowable_stress": getattr(
            material,
            "allowable_stress",
            None,
        ),

        "allowable_deflection": getattr(
            material,
            "allowable_deflection",
            None,
        ),

        "density": getattr(
            record,
            "density",
            None,
        ),

        "validation_status": getattr(
            record,
            "validation_status",
            None,
        ),

        "source": getattr(
            record,
            "source",
            None,
        ),
    }


# ============================================================
# PROFILE SERIALISATION
# ============================================================

def profile_to_dict(key: str, profile: Any) -> dict:

    if inspect.isfunction(profile):

        return {
            "key": key,
            "name": key,
            "type": profile.__name__,
            "parameters": {
                "width": "m",
                "thickness": "m",
            },
        }

    result = {
        "key": key,

        "name": getattr(
            profile,
            "name",
            getattr(
                profile,
                "designation",
                key,
            ),
        ),

        "designation": getattr(
            profile,
            "designation",
            None,
        ),

        "type": type(profile).__name__,
    }

    attributes = (
        "section_type",
        "area",
        "area_m2",
        "second_moment_of_area",
        "second_moment_of_area_x",
        "second_moment_of_area_y",
        "Ixx",
        "Iyy",
        "section_modulus",
        "section_modulus_x",
        "section_modulus_y",
        "Zxx",
        "Zyy",
        "shear_area",
        "mass_per_length",
        "width",
        "height",
        "thickness",
        "dimensions",
        "manufacturer",
        "source",
        "validation_status",
        "section_modulus_source",
    )

    for attribute in attributes:

        if hasattr(profile, attribute):

            try:
                result[attribute] = json_safe(
                    getattr(profile, attribute)
                )
            except Exception:
                result[attribute] = None

    return result


# ============================================================
# MATERIAL DATA
# ============================================================

def get_material_data():

    materials = available_materials()

    return {
        key: material_to_dict(
            key,
            record,
        )
        for key, record in materials.items()
    }


# ============================================================
# PROFILE DATA
# ============================================================

def get_profile_data():

    result = {}

    # --------------------------------------------------------
    # Generic rectangular profile
    # --------------------------------------------------------

    try:

        generic = available_profiles()

        rectangular = generic.get(
            "Rectangular panel strip"
        )

        if rectangular is not None:

            result[
                "Rectangular panel strip"
            ] = profile_to_dict(
                "Rectangular panel strip",
                rectangular,
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # Evergrip catalogue
    # --------------------------------------------------------

    if evergrip_profile_catalog is not None:

        try:

            catalogue = (
                evergrip_profile_catalog()
                if callable(
                    evergrip_profile_catalog
                )
                else evergrip_profile_catalog
            )

            # The current catalogue returns a list.
            if isinstance(catalogue, list):

                for profile in catalogue:

                    name = getattr(
                        profile,
                        "name",
                        None,
                    )

                    if not name:
                        continue

                    result[name] = profile_to_dict(
                        name,
                        profile,
                    )

            # Also support dictionary catalogues.
            elif isinstance(catalogue, dict):

                for key, profile in catalogue.items():

                    if isinstance(profile, dict):

                        result[str(key)] = {
                            "key": str(key),
                            "name": str(key),
                            "section_type": str(key),
                            "catalogue_profiles": {
                                profile_key:
                                profile_to_dict(
                                    profile_key,
                                    profile_value,
                                )
                                for profile_key,
                                profile_value
                                in profile.items()
                            },
                        }

                    else:

                        result[str(key)] = profile_to_dict(
                            str(key),
                            profile,
                        )

        except Exception:
            pass

    return result


# ============================================================
# PROFILE RESOLUTION
# ============================================================

def resolve_profile(
    profile_key: str,
    payload: dict,
):

    profile_key = str(profile_key).strip()

    # --------------------------------------------------------
    # Generic rectangular section
    # --------------------------------------------------------

    if (
        profile_key
        == "Rectangular panel strip"
    ):

        profiles = available_profiles()

        factory = profiles.get(
            "Rectangular panel strip"
        )

        if factory is None:
            raise ValueError(
                "Rectangular panel profile is unavailable."
            )

        width = float(
            payload.get(
                "width",
                1.0,
            )
        )

        thickness = float(
            payload.get(
                "thickness",
                0.05,
            )
        )

        return factory(
            width,
            thickness,
        )

    # --------------------------------------------------------
    # Evergrip catalogue
    # --------------------------------------------------------

    if evergrip_profile_catalog is not None:

        catalogue = (
            evergrip_profile_catalog()
            if callable(
                evergrip_profile_catalog
            )
            else evergrip_profile_catalog
        )

        if isinstance(catalogue, list):

            for profile in catalogue:

                if (
                    getattr(
                        profile,
                        "name",
                        None,
                    )
                    == profile_key
                ):
                    return profile

        elif isinstance(catalogue, dict):

            if profile_key in catalogue:
                return catalogue[profile_key]

            for group in catalogue.values():

                if isinstance(group, dict):

                    if profile_key in group:
                        return group[profile_key]

    raise ValueError(
        f"Unknown profile '{profile_key}'."
    )


# ============================================================
# MATERIAL RESOLUTION
# ============================================================

def resolve_material(
    material_key: str,
):

    materials = available_materials()

    if material_key not in materials:

        raise ValueError(
            f"Unknown material '{material_key}'."
        )

    return materials[material_key]


# ============================================================
# HTTP HANDLER
# ============================================================

class EngineeringAPIHandler(
    BaseHTTPRequestHandler
):

    server_version = (
        "GRPStructuralAssistant/1.0"
    )

    # --------------------------------------------------------
    # JSON RESPONSE
    # --------------------------------------------------------

    def send_json(
        self,
        data: Any,
        status: int = 200,
    ):

        payload = json.dumps(
            json_safe(data),
            indent=2,
            allow_nan=False,
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(payload)),
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )

        self.end_headers()

        self.wfile.write(payload)

    # --------------------------------------------------------
    # TEXT RESPONSE
    # --------------------------------------------------------

    def send_text(
        self,
        content: bytes,
        content_type: str,
        status: int = 200,
    ):

        self.send_response(status)

        self.send_header(
            "Content-Type",
            content_type,
        )

        self.send_header(
            "Content-Length",
            str(len(content)),
        )

        self.end_headers()

        self.wfile.write(content)

    # --------------------------------------------------------
    # REQUEST BODY
    # --------------------------------------------------------

    def read_json_body(self):

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

        except ValueError:

            content_length = 0

        if content_length <= 0:
            return {}

        raw = self.rfile.read(
            content_length
        )

        try:

            return json.loads(
                raw.decode("utf-8")
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                f"Invalid JSON request: {exc}"
            )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def do_GET(self):

        try:

            if self.path in (
                "/",
                "/index.html",
            ):

                file_path = (
                    FRONTEND_DIR
                    / "index.html"
                )

                self.send_text(
                    file_path.read_bytes(),
                    "text/html; charset=utf-8",
                )

                return

            if self.path == "/app.js":

                file_path = (
                    FRONTEND_DIR
                    / "app.js"
                )

                self.send_text(
                    file_path.read_bytes(),
                    "application/javascript; charset=utf-8",
                )

                return

            if self.path == "/style.css":

                file_path = (
                    FRONTEND_DIR
                    / "style.css"
                )

                self.send_text(
                    file_path.read_bytes(),
                    "text/css; charset=utf-8",
                )

                return

            if self.path == "/materials":

                self.send_json(
                    {
                        "materials":
                        get_material_data()
                    }
                )

                return

            if self.path == "/profiles":

                self.send_json(
                    {
                        "profiles":
                        get_profile_data()
                    }
                )

                return

            if self.path == "/health":

                self.send_json(
                    {
                        "status": "ok",
                        "service":
                        "GRP Structural Design Assistant",
                    }
                )

                return

            self.send_json(
                {
                    "error":
                    "Endpoint not found.",
                    "path": self.path,
                },
                status=404,
            )

        except Exception as exc:

            self.send_json(
                {
                    "error": str(exc),
                    "type":
                    type(exc).__name__,
                },
                status=500,
            )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def do_POST(self):

        if self.path != "/calculation":

            self.send_json(
                {
                    "error":
                    "Endpoint not found.",
                    "path": self.path,
                },
                status=404,
            )

            return

        try:

            payload = self.read_json_body()

            required = [
                "span",
                "tributary_width",
                "permanent_load",
                "imposed_load",
                "gamma_G",
                "gamma_Q",
                "material",
                "profile",
                "allowable_stress",
                "allowable_deflection",
            ]

            missing = [
                field
                for field in required
                if field not in payload
            ]

            if missing:

                self.send_json(
                    {
                        "success": False,
                        "error":
                        "Missing required input: "
                        + ", ".join(missing),
                        "missing": missing,
                    },
                    status=400,
                )

                return

            support_condition = payload.get(
                "support_condition",
                "simply_supported",
            )

            span = float(
                payload["span"]
            )

            tributary_width = float(
                payload["tributary_width"]
            )

            permanent_load = float(
                payload["permanent_load"]
            )

            imposed_load = float(
                payload["imposed_load"]
            )

            gamma_G = float(
                payload["gamma_G"]
            )

            gamma_Q = float(
                payload["gamma_Q"]
            )

            allowable_stress = float(
                payload["allowable_stress"]
            )

            allowable_deflection = float(
                payload["allowable_deflection"]
            )

            material_key = str(
                payload["material"]
            )

            profile_key = str(
                payload["profile"]
            )

            material_record = resolve_material(
                material_key
            )

            profile = resolve_profile(
                profile_key,
                payload,
            )

            calculation = (
                build_panel_calculation(
                    span=span,
                    tributary_width=tributary_width,
                    permanent_load=permanent_load,
                    imposed_load=imposed_load,
                    gamma_G=gamma_G,
                    gamma_Q=gamma_Q,
                    support_condition=support_condition,
                    material_record=material_record,
                    profile=profile,
                    allowable_stress=allowable_stress,
                    allowable_deflection=allowable_deflection,
                    shear_correction_factor=float(
                        payload.get(
                            "shear_correction_factor",
                            5 / 6,
                        )
                    ),
                )
            )

            result = json_safe(
                calculation
            )

            self.send_json(
                {
                    "success": True,
                    "calculation": result,
                }
            )

        except Exception as exc:

            self.send_json(
                {
                    "success": False,
                    "error": str(exc),
                    "error_type":
                    type(exc).__name__,
                },
                status=400,
            )


# ============================================================
# SERVER
# ============================================================

def run():

    host = "127.0.0.1"
    port = 8000

    server = ThreadingHTTPServer(
        (
            host,
            port,
        ),
        EngineeringAPIHandler,
    )

    print("")
    print("=" * 60)
    print(
        "GRP STRUCTURAL DESIGN ASSISTANT"
    )
    print("=" * 60)
    print("")
    print(
        f"Server running at:"
    )
    print(
        f"http://{host}:{port}"
    )
    print("")
    print(
        "Available endpoints:"
    )
    print("  GET  /")
    print("  GET  /materials")
    print("  GET  /profiles")
    print("  GET  /health")
    print("  POST /calculation")
    print("")
    print(
        "Press CTRL+C to stop."
    )
    print("")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("")
        print(
            "Server stopped."
        )

    finally:

        server.server_close()


if __name__ == "__main__":
    run()