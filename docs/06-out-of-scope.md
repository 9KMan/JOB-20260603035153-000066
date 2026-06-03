# 6. Out of Scope

This document explicitly defines the boundaries of the current project scope.
Items listed here are **intentionally excluded** and should not be implemented
unless a future plan revises this document.

## Purpose

Defining out-of-scope items accomplishes three goals:

1. **Prevents scope creep** — clearly communicates what will *not* be built.
2. **Aligns stakeholder expectations** — avoids ambiguity in planning reviews.
3. **Enables future work** — provides a starting point for subsequent plans
   that may revisit these decisions.

## Excluded Items

### 6.1 Mobile Applications

Native iOS, native Android, React Native, and Flutter clients are **not
included**. The deliverable is a **web application only**.

**Rationale:** The requirements specify a browser-based experience. Mobile
is deferred to a future iteration pending validation of the web product.

**Re-evaluate when:** Product receives a verified demand signal from target
users, or when web adoption justifies an investment in native clients.

---

### 6.2 Unspecified Third-Party Integrations

Only third-party services explicitly named in the requirements are in scope.
This includes, but is not limited to:

- CRM platforms (Salesforce, HubSpot, etc.)
- Marketing automation tools (Marketo, Mailchimp, etc.)
- Analytics suites beyond the chosen baseline
- Communication platforms (Slack, Teams, Discord) for notifications
- Payment processors beyond the designated provider
- Identity providers beyond the designated SSO solution
- ERP / accounting integrations
- Data warehouse / ETL pipelines

**Rationale:** Each third-party integration carries non-trivial
engineering, security review, and ongoing maintenance cost. They must be
justified individually with concrete user value.

**Re-evaluate when:** A specific integration is added to the requirements
with a documented use case and success metric.

---

### 6.3 Performance Optimization at Scale (1M+ Users)

The system is designed and tested for the **current target user base**.
Architectural choices that are only required beyond 1,000,000 concurrent
users are out of scope.

Examples of deferred work:

- Multi-region active-active deployment
- Database sharding across heterogeneous clusters
- Edge-computing and CDN logic beyond static asset delivery
- Real-time stream processing at internet-scale volumes
- Custom low-level performance engineering (kernel tuning, etc.)
- Advanced caching hierarchies (L1/L2/L3 application tiers)

**Rationale:** Premature optimization at this scale is a poor use of
engineering resources. Current projections do not justify the cost.

**Re-evaluate when:** User metrics indicate sustained growth trajectory
toward the 1M+ threshold, **and** business case is approved.

---

### 6.4 White-Label / Multi-Tenant Capabilities

The system is a **single-tenant** application serving one organization
(or one brand identity) per deployment.

Excluded multi-tenant features:

- Tenant isolation in shared infrastructure
- Per-tenant theming, branding, or domain mapping
- Tenant-scoped data partitioning
- Tenant administration consoles
- Per-tenant configuration and feature flags
- Tenant-aware billing or usage metering
- Subdomain or path-based tenant routing

**Rationale:** Multi-tenancy introduces significant complexity across the
stack (database, application, deployment, support) that is not warranted
by the current single-tenant requirement.

**Re-evaluate when:** A concrete multi-customer business model is adopted,
**and** the architectural migration plan is approved.

---

## Process for Adding In-Scope Items

If a stakeholder requests an item currently listed as out of scope:

1. **Open a proposal** documenting the use case, expected value, and
   rough cost estimate.
2. **Review** in the next planning cycle with engineering and product.
3. **If approved**, create a new plan (e.g., `PLAN-NN.md`) and remove
   the item from this document.
4. **If rejected**, document the decision and reasoning for future
   reference.

## Change Log

| Date       | Author          | Change                              |
|------------|-----------------|-------------------------------------|
| YYYY-MM-DD | Engineering     | Initial out-of-scope definition.    |

## Related Documents

- `PLAN-00.md` — Project overview and in-scope summary
- `docs/requirements.md` — Authoritative requirements source
- `docs/architecture.md` — Architectural decisions and constraints
