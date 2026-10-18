"use strict";

/* ============================================================
   GRP STRUCTURAL DESIGN ASSISTANT
   app.js
   ============================================================ */

/* ============================================================
   GLOBAL STATE
   ============================================================ */

let materials = {};
let profiles = {};
let lastCalculation = null;


/* ============================================================
   DOM HELPERS
   ============================================================ */

function $(id) {
    return document.getElementById(id);
}


function showElement(element) {
    if (!element) return;

    element.style.display = "";
    element.classList.remove("hidden");
}


function hideElement(element) {
    if (!element) return;

    element.style.display = "none";
    element.classList.add("hidden");
}


function setText(id, value) {
    const element = $(id);

    if (element) {
        element.textContent = value;
    }
}


function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================================
   NUMBER HELPERS
   ============================================================ */

function numberValue(id, fallback = null) {
    const element = $(id);

    if (!element) {
        return fallback;
    }

    const value = Number(element.value);

    if (!Number.isFinite(value)) {
        return fallback;
    }

    return value;
}


function formatNumber(value, decimals = 3) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toLocaleString("en-GB", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}


function formatPercent(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    let percent = number;

    if (Math.abs(percent) <= 2) {
        percent *= 100;
    }

    return `${formatNumber(percent, 1)}%`;
}


function utilisationNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return null;
    }

    if (Math.abs(number) > 2) {
        return number / 100;
    }

    return number;
}


/* ============================================================
   API
   ============================================================ */

async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const text = await response.text();

    let data = {};

    if (text.trim() !== "") {
        try {
            data = JSON.parse(text);
        } catch (error) {
            throw new Error(
                `Server returned invalid JSON from ${url}.`
            );
        }
    }

    if (!response.ok) {
        const message =
            data.error ||
            data.detail ||
            data.message ||
            `Request failed (${response.status}).`;

        throw new Error(message);
    }

    return data;
}


async function fetchFirstWorking(urls, options = {}) {
    let lastError = null;

    for (const url of urls) {
        try {
            return await fetchJson(url, options);
        } catch (error) {
            lastError = error;
        }
    }

    throw lastError || new Error(
        "Unable to connect to the engineering API."
    );
}


/* ============================================================
   MATERIALS
   ============================================================ */

async function loadMaterials() {
    const select = $("material");

    if (!select) {
        return;
    }

    select.innerHTML =
        '<option value="">Loading materials...</option>';

    try {
        const data = await fetchFirstWorking([
            "/materials",
            "/api/materials",
            "/api/material-library"
        ]);

        materials = data.materials || data || {};

        select.innerHTML = "";

        const entries = Object.entries(materials);

        if (entries.length === 0) {
            select.innerHTML =
                '<option value="">No materials available</option>';
            return;
        }

        for (const [key, record] of entries) {
            const option = document.createElement("option");

            option.value = key;

            const material =
                record?.material || record || {};

            const name =
                material.name ||
                record?.name ||
                key;

            const grade =
                record?.standard_grade ||
                record?.grade ||
                "";

            option.textContent =
                grade
                    ? `${name} — ${grade}`
                    : name;

            select.appendChild(option);
        }

        updateMaterialInfo();

    } catch (error) {
        select.innerHTML =
            '<option value="">Unable to load materials</option>';

        showError(
            `Unable to load materials: ${error.message}`
        );
    }
}


/* ============================================================
   MATERIAL INFORMATION
   ============================================================ */

function updateMaterialInfo() {
    const select = $("material");
    const panel = $("material-info");

    if (!select || !panel) {
        return;
    }

    const record = materials[select.value];

    if (!record) {
        panel.innerHTML = "";
        return;
    }

    const material =
        record.material || record;

    const youngs =
        material.youngs_modulus;

    const transverse =
        material.transverse_youngs_modulus;

    const shear =
        material.shear_modulus;

    const allowable =
        material.allowable_stress ||
        record.axial_flexural_strength ||
        record.axial_tensile_strength;

    panel.innerHTML = `
        <div class="info-title">
            Material information
        </div>

        <div class="info-grid">

            <div>
                <span>Manufacturer</span>
                <strong>
                    ${escapeHtml(
                        record.manufacturer || "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Product</span>
                <strong>
                    ${escapeHtml(
                        record.product || "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Grade</span>
                <strong>
                    ${escapeHtml(
                        record.standard_grade ||
                        record.grade ||
                        "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Young's modulus</span>
                <strong>
                    ${
                        youngs
                            ? `${formatNumber(
                                Number(youngs) / 1e9,
                                2
                            )} GPa`
                            : "—"
                    }
                </strong>
            </div>

            <div>
                <span>Transverse modulus</span>
                <strong>
                    ${
                        transverse
                            ? `${formatNumber(
                                Number(transverse) / 1e9,
                                2
                            )} GPa`
                            : "—"
                    }
                </strong>
            </div>

            <div>
                <span>Shear modulus</span>
                <strong>
                    ${
                        shear
                            ? `${formatNumber(
                                Number(shear) / 1e9,
                                2
                            )} GPa`
                            : "Not available"
                    }
                </strong>
            </div>

            <div>
                <span>Allowable/reference stress</span>
                <strong>
                    ${
                        allowable
                            ? `${formatNumber(
                                Number(allowable) / 1e6,
                                1
                            )} MPa`
                            : "—"
                    }
                </strong>
            </div>

            <div>
                <span>Density</span>
                <strong>
                    ${
                        record.density
                            ? `${formatNumber(
                                record.density,
                                0
                            )} kg/m³`
                            : "—"
                    }
                </strong>
            </div>

        </div>

        <div class="validation-note">
            ${escapeHtml(
                record.validation_status ||
                "Reference data — validate before engineering use."
            )}
        </div>
    `;
}


/* ============================================================
   PROFILE LOADING
   ============================================================ */

async function loadProfiles() {
    const typeSelect = $("profile-type");

    if (!typeSelect) {
        return;
    }

    typeSelect.innerHTML =
        '<option value="">Loading profiles...</option>';

    try {
        const data = await fetchFirstWorking([
            "/profiles",
            "/api/profiles",
            "/api/profile-library"
        ]);

        const raw =
            data.profiles || data || {};

        profiles = normaliseProfiles(raw);

        populateProfileTypes();

    } catch (error) {
        typeSelect.innerHTML =
            '<option value="">Unable to load profiles</option>';

        showError(
            `Unable to load profiles: ${error.message}`
        );
    }
}


/* ============================================================
   PROFILE NORMALISATION
   ============================================================ */

function normaliseProfiles(raw) {
    const result = {};

    result["Rectangular panel strip"] = {
        name: "Rectangular panel strip",
        rectangular: true,
        profiles: {}
    };


    if (Array.isArray(raw)) {
        for (const profile of raw) {
            if (!profile || typeof profile !== "object") {
                continue;
            }

            const type =
                profile.section_type ||
                profile.sectionType ||
                profile.profile_type ||
                profile.profileType ||
                "Other";

            const name =
                profile.name ||
                "Unnamed profile";

            if (!result[type]) {
                result[type] = {
                    name: type,
                    rectangular: false,
                    profiles: {}
                };
            }

            if (!result[type].profiles[name]) {
                result[type].profiles[name] = profile;
            }
        }

        return result;
    }


    if (
        raw &&
        typeof raw === "object"
    ) {
        for (const [key, value] of Object.entries(raw)) {

            if (
                !value ||
                typeof value !== "object"
            ) {
                continue;
            }


            if (
                value.profiles &&
                typeof value.profiles === "object"
            ) {
                const typeName =
                    value.name || key;

                if (
                    typeName ===
                    "Rectangular panel strip"
                ) {
                    continue;
                }

                if (!result[typeName]) {
                    result[typeName] = {
                        name: typeName,
                        rectangular: false,
                        profiles: {}
                    };
                }

                for (
                    const [
                        profileKey,
                        profileValue
                    ]
                    of Object.entries(value.profiles)
                ) {
                    if (
                        profileValue &&
                        typeof profileValue === "object"
                    ) {
                        const profileName =
                            profileValue.name ||
                            profileKey;

                        if (
                            !result[typeName]
                                .profiles[profileName]
                        ) {
                            result[typeName]
                                .profiles[profileName] =
                                profileValue;
                        }
                    }
                }

                continue;
            }


            const type =
                value.section_type ||
                value.sectionType ||
                value.profile_type ||
                value.profileType;

            if (type) {
                const name =
                    value.name ||
                    key;

                if (!result[type]) {
                    result[type] = {
                        name: type,
                        rectangular: false,
                        profiles: {}
                    };
                }

                if (
                    !result[type]
                        .profiles[name]
                ) {
                    result[type]
                        .profiles[name] =
                        value;
                }
            }
        }
    }

    return result;
}


/* ============================================================
   PROFILE TYPE DROPDOWN
   ============================================================ */

function populateProfileTypes() {
    const select = $("profile-type");

    if (!select) {
        return;
    }

    select.innerHTML = "";

    const optionPlaceholder =
        document.createElement("option");

    optionPlaceholder.value = "";
    optionPlaceholder.textContent =
        "Select profile type";

    select.appendChild(optionPlaceholder);


    const types = Object.keys(profiles);

    const uniqueTypes = [
        ...new Set(types)
    ];


    uniqueTypes.sort((a, b) => {
        if (
            a ===
            "Rectangular panel strip"
        ) {
            return -1;
        }

        if (
            b ===
            "Rectangular panel strip"
        ) {
            return 1;
        }

        return a.localeCompare(b);
    });


    for (const type of uniqueTypes) {
        const option =
            document.createElement("option");

        option.value = type;
        option.textContent = type;

        select.appendChild(option);
    }


    if (uniqueTypes.length > 0) {
        select.value =
            "Rectangular panel strip";

        updateProfileInterface();
    }
}


/* ============================================================
   PROFILE INTERFACE
   ============================================================ */

function updateProfileInterface() {
    const typeSelect = $("profile-type");

    if (!typeSelect) {
        return;
    }

    const rectangularFields =
        $("rectangular-profile-fields") ||
        $("rectangular-inputs");

    const manufacturerFields =
        $("manufacturer-profile-fields") ||
        $("manufacturer-profile-inputs");

    const profileSelect =
        $("profile");

    const type =
        typeSelect.value;


    if (!type) {
        hideElement(rectangularFields);
        hideElement(manufacturerFields);
        return;
    }


    if (
        type ===
        "Rectangular panel strip"
    ) {
        showElement(rectangularFields);
        hideElement(manufacturerFields);

        updateProfileInfo();

        return;
    }


    hideElement(rectangularFields);
    showElement(manufacturerFields);


    if (!profileSelect) {
        return;
    }

    profileSelect.innerHTML = "";


    const typeRecord =
        profiles[type];

    if (
        !typeRecord ||
        !typeRecord.profiles
    ) {
        profileSelect.innerHTML =
            '<option value="">No profiles available</option>';

        updateProfileInfo();
        return;
    }


    const entries =
        Object.entries(
            typeRecord.profiles
        );


    const unique =
        new Map();

    for (
        const [
            key,
            profile
        ]
        of entries
    ) {
        const name =
            profile?.name ||
            key;

        if (!unique.has(name)) {
            unique.set(name, profile);
        }
    }


    for (
        const [
            name,
            profile
        ]
        of unique
    ) {
        const option =
            document.createElement("option");

        option.value = name;

        option.textContent = name;

        profileSelect.appendChild(option);
    }


    updateProfileInfo();
}


/* ============================================================
   PROFILE INFORMATION
   ============================================================ */

function updateProfileInfo() {
    const typeSelect =
        $("profile-type");

    const profileSelect =
        $("profile");

    const panel =
        $("profile-info");

    if (!typeSelect || !panel) {
        return;
    }

    const type =
        typeSelect.value;


    if (
        type ===
        "Rectangular panel strip"
    ) {
        panel.innerHTML = `
            <div class="info-title">
                Profile information
            </div>

            <div class="validation-note">
                User-defined rectangular panel strip.
                Enter width and thickness below.
            </div>
        `;

        return;
    }


    if (!profileSelect) {
        panel.innerHTML = "";
        return;
    }


    const typeRecord =
        profiles[type];

    if (
        !typeRecord ||
        !typeRecord.profiles
    ) {
        panel.innerHTML = "";
        return;
    }


    const record =
        typeRecord.profiles[
            profileSelect.value
        ];


    if (!record) {
        panel.innerHTML = "";
        return;
    }


    const properties =
        record.section_properties ||
        record.properties ||
        record;


    const rows = [];

    const fields = [
        ["area", "Area", "m²"],
        ["area_m2", "Area", "m²"],
        [
            "second_moment_of_area_x",
            "Ixx",
            "m⁴"
        ],
        [
            "second_moment_of_area",
            "Ixx",
            "m⁴"
        ],
        ["Ixx", "Ixx", "m⁴"],
        [
            "second_moment_of_area_y",
            "Iyy",
            "m⁴"
        ],
        ["Iyy", "Iyy", "m⁴"],
        [
            "section_modulus_x",
            "Zxx",
            "m³"
        ],
        [
            "section_modulus",
            "Zxx",
            "m³"
        ],
        ["Zxx", "Zxx", "m³"],
        [
            "section_modulus_y",
            "Zyy",
            "m³"
        ],
        ["mass_per_length", "Mass", "kg/m"]
    ];


    const displayed =
        new Set();


    for (
        const [
            key,
            label,
            unit
        ]
        of fields
    ) {
        if (displayed.has(label)) {
            continue;
        }

        const value =
            properties[key];

        if (
            value !== undefined &&
            value !== null &&
            Number.isFinite(Number(value))
        ) {
            rows.push(`
                <div>
                    <span>
                        ${label}
                    </span>

                    <strong>
                        ${formatNumber(
                            Number(value),
                            6
                        )}
                        ${unit}
                    </strong>
                </div>
            `);

            displayed.add(label);
        }
    }


    panel.innerHTML = `
        <div class="info-title">
            Profile information
        </div>

        <div class="info-grid">

            <div>
                <span>Profile</span>
                <strong>
                    ${escapeHtml(
                        record.name ||
                        profileSelect.value
                    )}
                </strong>
            </div>

            ${rows.join("")}

        </div>

        <div class="validation-note">
            ${escapeHtml(
                record.validation_status ||
                record.source ||
                "Profile data must be validated against manufacturer documentation."
            )}
        </div>
    `;
}


/* ============================================================
   INPUT VALIDATION
   ============================================================ */

function validateInputs() {
    const required = [
        ["span", "Span"],
        [
            "tributary-width",
            "Tributary width"
        ],
        [
            "permanent-load",
            "Permanent load"
        ],
        [
            "imposed-load",
            "Imposed load"
        ],
        ["gamma-g", "γG"],
        ["gamma-q", "γQ"]
    ];


    for (
        const [
            id,
            label
        ]
        of required
    ) {
        const value =
            numberValue(id);

        if (
            value === null ||
            value < 0
        ) {
            throw new Error(
                `${label} must be a valid non-negative number.`
            );
        }
    }


    if (
        numberValue("span") <= 0
    ) {
        throw new Error(
            "Span must be greater than zero."
        );
    }


    if (
        numberValue("tributary-width") <= 0
    ) {
        throw new Error(
            "Tributary width must be greater than zero."
        );
    }


    if (
        numberValue("gamma-g") <= 0 ||
        numberValue("gamma-q") <= 0
    ) {
        throw new Error(
            "Load factors must be greater than zero."
        );
    }


    if (!$("material")?.value) {
        throw new Error(
            "Please select a material."
        );
    }


    if (!$("profile-type")?.value) {
        throw new Error(
            "Please select a profile type."
        );
    }


    const type =
        $("profile-type").value;


    if (
        type ===
        "Rectangular panel strip"
    ) {
        const width =
            numberValue("profile-width") ??
            numberValue("width");

        const thickness =
            numberValue("profile-thickness") ??
            numberValue("thickness");


        if (
            width === null ||
            width <= 0 ||
            thickness === null ||
            thickness <= 0
        ) {
            throw new Error(
                "Profile width and thickness must be greater than zero."
            );
        }

    } else {

        if (!$("profile")?.value) {
            throw new Error(
                "Please select a manufacturer profile."
            );
        }
    }
}


/* ============================================================
   CALCULATION PAYLOAD
   ============================================================ */

function buildCalculationPayload() {
    const profileType =
        $("profile-type")?.value || "";


    const payload = {
        span:
            numberValue("span"),

        tributary_width:
            numberValue("tributary-width"),

        permanent_load:
            numberValue("permanent-load"),

        imposed_load:
            numberValue("imposed-load"),

        gamma_G:
            numberValue("gamma-g"),

        gamma_Q:
            numberValue("gamma-q"),

        support_condition:
            $("support-condition")?.value ||
            "simply_supported",

        material:
            $("material")?.value || "",

        material_name:
            $("material")?.value || "",

        profile_type:
            profileType,

        profile:
            $("profile")?.value || null
    };


    if (
        profileType ===
        "Rectangular panel strip"
    ) {
        payload.width =
            numberValue("profile-width") ??
            numberValue("width");

        payload.thickness =
            numberValue("profile-thickness") ??
            numberValue("thickness");
    }


    const allowableStress =
        numberValue("allowable-stress");

    if (allowableStress !== null) {
        payload.allowable_stress =
            allowableStress;
    }


    const allowableDeflection =
        numberValue("allowable-deflection");

    if (allowableDeflection !== null) {
        payload.allowable_deflection =
            allowableDeflection;
    }


    const shearFactor =
        numberValue(
            "shear-correction-factor"
        );

    if (shearFactor !== null) {
        payload.shear_correction_factor =
            shearFactor;
    }


    return payload;
}


/* ============================================================
   RUN CALCULATION
   ============================================================ */

async function runCalculation() {
    hideError();

    const button =
        $("calculate-button");


    try {
        validateInputs();

        const payload =
            buildCalculationPayload();


        if (button) {
            button.disabled = true;
            button.textContent =
                "Calculating...";
        }


        const result =
            await fetchFirstWorking(
                [
                    "/calculate",
                    "/api/calculate",
                    "/calculation"
                ],
                {
                    method: "POST",
                    body:
                        JSON.stringify(payload)
                }
            );


        lastCalculation =
            result;


        renderResults(result);

    } catch (error) {

        showError(
            error.message ||
            "Calculation failed."
        );

    } finally {

        if (button) {
            button.disabled = false;
            button.textContent =
                "Run calculation";
        }
    }
}


/* ============================================================
   RESULT HELPERS
   ============================================================ */

function findValue(object, keys) {
    if (
        !object ||
        typeof object !== "object"
    ) {
        return null;
    }

    for (const key of keys) {
        if (
            object[key] !== undefined &&
            object[key] !== null
        ) {
            return object[key];
        }
    }

    return null;
}


function extractResults(result) {
    const calculation =
        result.calculation ||
        result;


    const uls =
        calculation.uls_results ||
        calculation.uls ||
        calculation.ULS ||
        calculation.uls_design ||
        {};

    const sls =
        calculation.sls_results ||
        calculation.sls ||
        calculation.SLS ||
        calculation.sls_design ||
        {};

    const stressCheck =
        calculation.uls_stress_check ||
        calculation.stress_check ||
        uls.stress_check ||
        {};

    const deflectionCheck =
        calculation.sls_deflection_check ||
        calculation.deflection_check ||
        sls.deflection_check ||
        {};


    const ulsUtil =
        findValue(
            stressCheck,
            [
                "utilisation",
                "utilization",
                "utilisation_ratio",
                "utilization_ratio"
            ]
        );


    const slsUtil =
        findValue(
            deflectionCheck,
            [
                "utilisation",
                "utilization",
                "utilisation_ratio",
                "utilization_ratio"
            ]
        );


    const explicit =
        findValue(
            calculation,
            [
                "governing_utilisation",
                "governing_utilization"
            ]
        );


    const ulsNumber =
        utilisationNumber(ulsUtil);

    const slsNumber =
        utilisationNumber(slsUtil);


    let governing = null;


    if (explicit !== null) {
        governing =
            utilisationNumber(explicit);
    } else {

        const values = [
            ulsNumber,
            slsNumber
        ].filter(
            value => value !== null
        );

        if (values.length) {
            governing =
                Math.max(...values);
        }
    }


    const explicitPass =
        calculation.overall_pass ??
        calculation.pass;


    const overallPass =
        explicitPass !== undefined
            ? Boolean(explicitPass)
            : governing === null
                ? null
                : governing <= 1;


    return {
        calculation,
        uls,
        sls,
        stressCheck,
        deflectionCheck,
        ulsUtil,
        slsUtil,
        governing,
        overallPass
    };
}


/* ============================================================
   RENDER RESULTS
   ============================================================ */

function renderResults(result) {
    const data =
        extractResults(result);

    const calculation =
        data.calculation;

    const results =
        $("results");

    if (!results) {
        return;
    }


    showElement(results);


    const status =
        data.overallPass === null
            ? "—"
            : data.overallPass
                ? "PASS"
                : "FAIL";


    setText(
        "result-status",
        status
    );


    setText(
        "result-summary",
        buildResultSummary(calculation)
    );


    setText(
        "calculation-id",
        calculation.calculation_id ||
        calculation.id ||
        generateCalculationId()
    );


    setText(
        "uls-utilisation",
        formatPercent(data.ulsUtil)
    );


    setText(
        "sls-utilisation",
        formatPercent(data.slsUtil)
    );


    setText(
        "governing-utilisation",
        formatPercent(data.governing)
    );


    setText(
        "governing-utilisation-detail",
        formatPercent(data.governing)
    );


    setText(
        "governing-check",
        determineGoverningCheck(data)
    );


    renderCalculationDetails(
        calculation,
        data
    );


    renderMaterialStatus(calculation);

    renderProfileSource(calculation);

    renderAssumptions(calculation);

    renderWarnings(calculation);

    renderUtilisationBars(data);
}


/* ============================================================
   RESULT SUMMARY
   ============================================================ */

function buildResultSummary(result) {
    const input =
        result.inputs ||
        result.input ||
        {};


    const material =
        input.material_name ||
        result.material_name ||
        $("material")?.value ||
        "Selected material";


    const profile =
        input.profile_name ||
        result.profile_name ||
        $("profile")?.value ||
        $("profile-type")?.value ||
        "Selected profile";


    return `${material} — ${profile}`;
}


/* ============================================================
   GOVERNING CHECK
   ============================================================ */

function determineGoverningCheck(data) {
    const uls =
        utilisationNumber(
            data.ulsUtil
        );

    const sls =
        utilisationNumber(
            data.slsUtil
        );


    if (
        uls === null &&
        sls === null
    ) {
        return "—";
    }


    if (
        sls !== null &&
        (
            uls === null ||
            sls >= uls
        )
    ) {
        return "SLS deflection";
    }


    return "ULS stress";
}


/* ============================================================
   DETAILED RESULTS
   ============================================================ */

function renderCalculationDetails(
    result,
    data
) {
    const panel =
        $("calculation-details");

    if (!panel) {
        return;
    }


    const input =
        result.inputs ||
        result.input ||
        {};


    const uls =
        data.uls;

    const stress =
        data.stressCheck;

    const deflection =
        data.deflectionCheck;


    panel.innerHTML = `

        <div class="detail-grid">

            <div>
                <span>Support condition</span>
                <strong>
                    ${escapeHtml(
                        input.support_condition ||
                        $("support-condition")?.value ||
                        "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Span</span>
                <strong>
                    ${formatNumber(
                        input.span ??
                        numberValue("span"),
                        3
                    )} m
                </strong>
            </div>

            <div>
                <span>Tributary width</span>
                <strong>
                    ${formatNumber(
                        input.tributary_width ??
                        numberValue(
                            "tributary-width"
                        ),
                        3
                    )} m
                </strong>
            </div>

            <div>
                <span>Permanent load</span>
                <strong>
                    ${formatNumber(
                        input.permanent_load ??
                        numberValue(
                            "permanent-load"
                        ),
                        1
                    )} N/m²
                </strong>
            </div>

            <div>
                <span>Imposed load</span>
                <strong>
                    ${formatNumber(
                        input.imposed_load ??
                        numberValue(
                            "imposed-load"
                        ),
                        1
                    )} N/m²
                </strong>
            </div>

            <div>
                <span>ULS line load</span>
                <strong>
                    ${formatEngineeringValue(
                        findValue(
                            uls,
                            [
                                "distributed_load",
                                "total_line_load",
                                "line_load",
                                "design_line_load"
                            ]
                        ),
                        "N/m"
                    )}
                </strong>
            </div>

            <div>
                <span>Total ULS load</span>
                <strong>
                    ${formatEngineeringValue(
                        findValue(
                            uls,
                            [
                                "total_load"
                            ]
                        ),
                        "N"
                    )}
                </strong>
            </div>

            <div>
                <span>Maximum bending moment</span>
                <strong>
                    ${formatEngineeringValue(
                        findValue(
                            uls,
                            [
                                "max_bending_moment",
                                "maximum_bending_moment",
                                "maximum_moment",
                                "max_moment",
                                "moment"
                            ]
                        ),
                        "N·m"
                    )}
                </strong>
            </div>

            <div>
                <span>Maximum shear</span>
                <strong>
                    ${formatEngineeringValue(
                        findValue(
                            uls,
                            [
                                "max_shear",
                                "maximum_shear",
                                "shear"
                            ]
                        ),
                        "N"
                    )}
                </strong>
            </div>

            <div>
                <span>Bending stress</span>
                <strong>
                    ${formatStress(
                        findValue(
                            stress,
                            [
                                "calculated_value",
                                "stress",
                                "bending_stress",
                                "maximum_stress"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>Allowable stress</span>
                <strong>
                    ${formatStress(
                        findValue(
                            stress,
                            [
                                "allowable_value",
                                "allowable_stress",
                                "limit"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>Stress utilisation</span>
                <strong>
                    ${formatPercent(
                        data.ulsUtil
                    )}
                </strong>
            </div>

            <div>
                <span>Maximum bending deflection</span>
                <strong>
                    ${formatDeflection(
                        findValue(
                            data.sls,
                            [
                                "bending_deflection"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>Shear deflection</span>
                <strong>
                    ${formatDeflection(
                        findValue(
                            data.sls,
                            [
                                "shear_deflection"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>Total maximum deflection</span>
                <strong>
                    ${formatDeflection(
                        findValue(
                            data.sls,
                            [
                                "max_deflection",
                                "maximum_deflection",
                                "deflection"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>Allowable deflection</span>
                <strong>
                    ${formatDeflection(
                        findValue(
                            deflection,
                            [
                                "allowable_value",
                                "allowable_deflection",
                                "limit"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>Deflection utilisation</span>
                <strong>
                    ${formatPercent(
                        data.slsUtil
                    )}
                </strong>
            </div>

            <div>
                <span>ULS stress check</span>
                <strong>
                    ${formatCheckStatus(
                        findValue(
                            stress,
                            [
                                "passes",
                                "pass"
                            ]
                        )
                    )}
                </strong>
            </div>

            <div>
                <span>SLS deflection check</span>
                <strong>
                    ${formatCheckStatus(
                        findValue(
                            deflection,
                            [
                                "passes",
                                "pass"
                            ]
                        )
                    )}
                </strong>
            </div>

        </div>
    `;
}


/* ============================================================
   MATERIAL STATUS
   ============================================================ */

function renderMaterialStatus(result) {
    const panel =
        $("result-material-status");

    if (!panel) {
        return;
    }


    const input =
        result.inputs ||
        result.input ||
        {};


    const record =
        materials[
            $("material")?.value
        ];


    const material =
        record?.material ||
        record ||
        {};


    panel.innerHTML = `
        <div class="detail-grid">

            <div>
                <span>Material</span>
                <strong>
                    ${escapeHtml(
                        input.material_name ||
                        material.name ||
                        $("material")?.value ||
                        "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Manufacturer</span>
                <strong>
                    ${escapeHtml(
                        input.material_manufacturer ||
                        record?.manufacturer ||
                        "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Grade</span>
                <strong>
                    ${escapeHtml(
                        input.material_grade ||
                        record?.standard_grade ||
                        record?.grade ||
                        "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Validation status</span>
                <strong>
                    ${escapeHtml(
                        input.material_validation_status ||
                        record?.validation_status ||
                        "Reference data — validate before engineering use."
                    )}
                </strong>
            </div>

        </div>
    `;
}


/* ============================================================
   PROFILE SOURCE
   ============================================================ */

function renderProfileSource(result) {
    const panel =
        $("result-profile-source");

    if (!panel) {
        return;
    }


    const input =
        result.inputs ||
        result.input ||
        {};


    panel.innerHTML = `
        <div class="detail-grid">

            <div>
                <span>Profile</span>
                <strong>
                    ${escapeHtml(
                        input.profile_name ||
                        $("profile")?.value ||
                        $("profile-type")?.value ||
                        "—"
                    )}
                </strong>
            </div>

            <div>
                <span>Source</span>
                <strong>
                    ${escapeHtml(
                        input.profile_source ||
                        "User-defined / API profile library"
                    )}
                </strong>
            </div>

            <div>
                <span>Validation status</span>
                <strong>
                    ${escapeHtml(
                        input.profile_validation_status ||
                        "Profile data must be validated against manufacturer documentation."
                    )}
                </strong>
            </div>

        </div>
    `;
}


/* ============================================================
   ASSUMPTIONS
   ============================================================ */

function renderAssumptions(result) {
    const list =
        $("assumptions");

    if (!list) {
        return;
    }


    const assumptions =
        Array.isArray(result.assumptions)
            ? result.assumptions
            : [];


    if (assumptions.length === 0) {
        list.innerHTML =
            "<li>No assumptions returned.</li>";
        return;
    }


    list.innerHTML =
        assumptions
            .map(
                item =>
                    `<li>${escapeHtml(item)}</li>`
            )
            .join("");
}


/* ============================================================
   WARNINGS
   ============================================================ */

function renderWarnings(result) {
    const list =
        $("warnings");

    if (!list) {
        return;
    }


    const warnings =
        Array.isArray(result.warnings)
            ? result.warnings
            : [];


    if (warnings.length === 0) {
        list.innerHTML =
            "<li>None returned by calculation.</li>";
        return;
    }


    list.innerHTML =
        warnings
            .map(
                item =>
                    `<li>${escapeHtml(item)}</li>`
            )
            .join("");
}


/* ============================================================
   UTILISATION VISUALS
   ============================================================ */

function renderUtilisationBars(data) {
    const resultDetails =
        $("calculation-details");

    if (!resultDetails) {
        return;
    }


    const old =
        $("utilisation-visuals");

    if (old) {
        old.remove();
    }


    const container =
        document.createElement("div");

    container.id =
        "utilisation-visuals";

    container.className =
        "utilisation-visuals";


    container.innerHTML = `
        <h3>Utilisation summary</h3>

        ${utilisationBar(
            "ULS stress",
            utilisationNumber(data.ulsUtil)
        )}

        ${utilisationBar(
            "SLS deflection",
            utilisationNumber(data.slsUtil)
        )}

        ${utilisationBar(
            "Governing",
            data.governing
        )}
    `;


    resultDetails.prepend(container);
}


function utilisationBar(label, value) {
    if (
        value === null ||
        value === undefined
    ) {
        return `
            <div class="utilisation-row">

                <div class="utilisation-label">
                    ${escapeHtml(label)}
                </div>

                <div class="utilisation-track">
                    <div
                        class="utilisation-fill"
                        style="width:0%;"
                    ></div>
                </div>

                <div class="utilisation-value">
                    —
                </div>

            </div>
        `;
    }


    const percent =
        Math.max(
            0,
            Math.min(
                100,
                value * 100
            )
        );


    return `
        <div class="utilisation-row">

            <div class="utilisation-label">
                ${escapeHtml(label)}
            </div>

            <div class="utilisation-track">

                <div
                    class="utilisation-fill"
                    style="width:${percent}%;"
                ></div>

            </div>

            <div class="utilisation-value">
                ${formatPercent(value)}
            </div>

        </div>
    `;
}


/* ============================================================
   FORMATTING
   ============================================================ */

function formatEngineeringValue(
    value,
    unit
) {
    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return `${formatNumber(
        number,
        3
    )} ${unit}`;
}


function formatStress(value) {
    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return `${formatNumber(
        number / 1e6,
        2
    )} MPa`;
}


function formatDeflection(value) {
    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return `${formatNumber(
        number * 1000,
        2
    )} mm`;
}


function formatCheckStatus(value) {
    if (value === true) {
        return "PASS";
    }

    if (value === false) {
        return "FAIL";
    }

    return "—";
}


/* ============================================================
   ERROR HANDLING
   ============================================================ */

function showError(message) {
    const error =
        $("error-message") ||
        $("error");

    if (!error) {
        return;
    }

    error.textContent =
        message;

    error.style.display =
        "block";

    error.classList.remove(
        "hidden"
    );
}


function hideError() {
    const error =
        $("error-message") ||
        $("error");

    if (!error) {
        return;
    }

    error.textContent =
        "";

    error.style.display =
        "none";

    error.classList.add(
        "hidden"
    );
}


/* ============================================================
   CALCULATION ID
   ============================================================ */

function generateCalculationId() {
    const now =
        new Date();

    const date =
        now.toISOString()
            .replace(
                /[-:TZ.]/g,
                ""
            )
            .slice(
                0,
                14
            );

    const random =
        Math.floor(
            1000 +
            Math.random() * 9000
        );

    return `GRP-${date}-${random}`;
}


/* ============================================================
   EVENT HANDLERS
   ============================================================ */

function initialiseEvents() {
    const form =
        $("calculation-form");


    if (form) {
        form.addEventListener(
            "submit",
            function (event) {
                event.preventDefault();
                runCalculation();
            }
        );
    }


    const button =
        $("calculate-button");


    if (
        button &&
        !form
    ) {
        button.addEventListener(
            "click",
            runCalculation
        );
    }


    const material =
        $("material");


    if (material) {
        material.addEventListener(
            "change",
            updateMaterialInfo
        );
    }


    const profileType =
        $("profile-type");


    if (profileType) {
        profileType.addEventListener(
            "change",
            updateProfileInterface
        );
    }


    const profile =
        $("profile");


    if (profile) {
        profile.addEventListener(
            "change",
            updateProfileInfo
        );
    }
}


/* ============================================================
   APPLICATION START
   ============================================================ */

async function initialiseApplication() {
    initialiseEvents();

    hideError();

    await Promise.all([
        loadMaterials(),
        loadProfiles()
    ]);
}


document.addEventListener(
    "DOMContentLoaded",
    initialiseApplication
);