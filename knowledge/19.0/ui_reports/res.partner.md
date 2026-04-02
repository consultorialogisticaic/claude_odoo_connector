# UI Report: res.partner

**Odoo Version:** 19.0
**Focus:** Colombian localization fields (NIT, l10n_co, l10n_latam)
**Sources:**
- Base: `odoo/odoo/addons/base/models/res_partner.py`
- LATAM: `odoo/addons/l10n_latam_base/models/res_partner.py`
- Colombia EDI: `enterprise/l10n_co_edi/models/res_partner.py`
- Colombia DIAN: `enterprise/l10n_co_dian/models/res_partner.py`

## Model Definition

| Attribute | Value |
|---|---|
| `_name` | `res.partner` |
| `_description` | `Contact` |
| `_rec_name` | `name` (default, uses `display_name` computed) |
| `_rec_names_search` | `['complete_name', 'email', 'ref', 'vat', 'company_registry']` |
| `_order` | `complete_name ASC, id desc` |

## Core Fields for CSV

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `name` | Char | Yes | — | Partner name. |
| `company_type` | Selection | No | — | `person` or `company`. Sets `is_company`. |
| `is_company` | Boolean | No | `False` | |
| `parent_id` | Many2one → `res.partner` | No | — | Parent company for contacts. |
| `type` | Selection | No | `contact` | `contact`, `invoice`, `delivery`, `other`, `private`. |
| `street` | Char | No | — | |
| `street2` | Char | No | — | |
| `city` | Char | No | — | |
| `state_id` | Many2one → `res.country.state` | No | — | |
| `zip` | Char | No | — | |
| `country_id` | Many2one → `res.country` | No | — | |
| `email` | Char | No | — | |
| `phone` | Char | No | — | |
| `mobile` | Char | No | — | |
| `website` | Char | No | — | |
| `ref` | Char | No | — | Internal Reference. |
| `lang` | Selection | No | — | Language code (e.g., `es_CO`). |
| `category_id` | Many2many → `res.partner.category` | No | — | Tags. |
| `customer_rank` | Integer | No | 0 | > 0 means customer. |
| `supplier_rank` | Integer | No | 0 | > 0 means vendor/supplier. |
| `property_payment_term_id` | Many2one → `account.payment.term` | No | — | Customer payment terms. Company-dependent. |
| `property_supplier_payment_term_id` | Many2one → `account.payment.term` | No | — | Vendor payment terms. Company-dependent. |
| `property_account_position_id` | Many2one → `account.fiscal.position` | No | — | Fiscal position. Company-dependent. |
| `property_account_receivable_id` | Many2one → `account.account` | No | — | Company-dependent. |
| `property_account_payable_id` | Many2one → `account.account` | No | — | Company-dependent. |

## Colombian Localization Fields (l10n_latam_base)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `l10n_latam_identification_type_id` | Many2one → `l10n_latam.identification.type` | No | `l10n_latam_base.it_vat` | The type of identification document. For Colombia: RUT, Cedula, NIT, etc. |
| `vat` | Char | No | — | Overridden label: "Identification Number". For Colombian RUT/NIT, includes verification digit (e.g., `900123456-7`). |
| `is_vat` | Boolean | — | related | Related to `l10n_latam_identification_type_id.is_vat`. |

## Colombian EDI Fields (l10n_co_edi)

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `l10n_co_edi_large_taxpayer` | Boolean | No | `False` | "Gran Contribuyente". |
| `l10n_co_edi_fiscal_regimen` | Selection | Yes | `48` (IVA) | `48`=IVA, `49`=No Aplica, `04`=IC, `ZA`=IVA en IC. |
| `l10n_co_edi_commercial_name` | Char | No | — | Commercial/trade name. |
| `l10n_co_edi_obligation_type_ids` | Many2many → `l10n_co_edi.type_code` | No | — | Tax obligations (Responsabilidades). |

## Colombian Identification Types

The `l10n_latam.identification.type` model includes Colombian document codes (`l10n_co_document_code`):
- `rut` — RUT (NIT with verification digit)
- `id_card` — Tarjeta de Identidad
- `national_citizen_id` — Cedula de Ciudadania
- `passport` — Pasaporte
- `foreign_id_card` — Cedula de Extranjeria
- `PEP` — Permiso Especial de Permanencia
- `PPT` — Permiso por Proteccion Temporal

## VAT/NIT Format for Colombia

- NIT format: `900123456-7` (9 digits + dash + verification digit)
- The `_get_vat_without_verification_code()` method strips the verification digit.
- The `_get_vat_verification_code()` method extracts just the verification digit.
- For `Consumidor Final`: special VAT `222222222222`.

## Constraints

- `vat` validation is handled by `_check_vat()`. For LATAM partners, only checks if `l10n_latam_identification_type_id.is_vat` is True.
- `_onchange_country_id`: Auto-sets identification type based on country.

## create() / write() Overrides

- Base `res.partner` has extensive `create()`/`write()` logic for commercial fields syncing, parent company propagation, etc.
- No specific `create()`/`write()` overrides in l10n_co_edi or l10n_co_dian for partner creation.
- `_inverse_vat` on `l10n_latam_identification_type_id` triggers VAT validation.

## Demo Data Patterns

Standard Odoo demo data creates partners via `base/demo/res.partner.csv` and module-specific demos. Colombian partners typically need:
```
name,is_company,company_type,vat,l10n_latam_identification_type_id,l10n_co_edi_fiscal_regimen,country_id,city,state_id
Proveedor ABC,True,company,900123456-7,NIT,48,Colombia,Bogota,Cundinamarca
```

## CSV Recommendations

- **Identity**: Use `name` for companies, or `name` + `parent_id` for contacts under companies.
- **Colombian fields**: Set `country_id` to Colombia first (triggers `_onchange_country_id` which sets identification type). Then set `l10n_latam_identification_type_id` and `vat`.
- **l10n_latam_identification_type_id**: FK lookup by name. Common values: "NIT", "Cedula de ciudadania", "Pasaporte".
- **l10n_co_edi_fiscal_regimen**: Use the code value (`48`, `49`, `04`, `ZA`), not the label.
- **l10n_co_edi_obligation_type_ids**: Many2many to `l10n_co_edi.type_code`. Common codes: `O-13` (Gran contribuyente), `O-15` (Autoretenedor), `O-23` (Agente retencion IVA), `O-47` (Regimen simple), `R-99-PN` (No aplica).
- **customer_rank/supplier_rank**: Set to 1 to mark as customer/supplier.
- Load companies before contacts (contacts reference parent_id).

## Recommended Identity Key for csv_loader

```
"res.partner": ["name", "is_company"]
```

Note: Partner names are not unique in Odoo. For demo data, `name` + `is_company` provides reasonable dedup. For contacts under a company, use `name` + `parent_id`. The csv_loader's `name_search` fallback handles most cases.
