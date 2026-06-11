---
name: fabric-project-access
description: >
  Use this skill whenever setting up access rights, user accounts, Entra ID groups, service
  principals, licences, Azure Key Vault, or role assignments for a new Pingala Fabric project.
  Triggers on phrases like "set up access for Fabric", "create Entra ID groups", "what access
  do we need", "provision users for Fabric project", "service principal setup", "Key Vault for
  Fabric", "Fabric licences", "workspace roles", "onboard a new Fabric customer", or any mention
  of user provisioning, guest users, ext_ accounts, security groups, or Fabric admin portal
  settings in the context of starting a new project. Also trigger when someone asks "what do we
  need from the customer to get started", "what access requests should we send", or wants to
  draft an access-request email for a customer. This skill covers Phase 1 of the Pingala Project
  Playbook — use it even if the user only asks about one part (e.g. just Entra ID groups, just
  licences, or just the service principal).
---

# Fabric Project Access Skill

This skill defines the complete set of access rights, user accounts, Entra ID groups, service
principals, licences, Key Vault configuration, and role assignments that Pingala needs from a
customer to start a Fabric / DataHub project.

It is the detailed reference for **Phase 1 — Users & Access** of the Pingala Project Playbook.

---

## Overview

Setting up access for a Fabric project involves seven workstreams. They can be requested from
the customer in parallel but all must be completed before Fabric configuration can begin.

```
1. Azure DevOps project
2. Guest user accounts (Pingala identities)
3. External user accounts (customer tenant, ext_ accounts)
4. Service Principal (App Registration)
5. Azure Key Vault
6. Licences
7. Entra ID security groups
8. Role & permission assignments
```

---

## 1 — Azure DevOps Project

The customer must create (or allow Pingala to create) an Azure DevOps project for the
engagement. This project is used for backlog management, sprint planning, source control
(Git repos), and time-registration integration with Pingala's D365 F&O.

**What to request from the customer:**

- A new Azure DevOps project (or confirmation Pingala may create one)
- The Pingala DevOps/integration resource (see section 2) must be granted
  **Project Collection Administrator** rights at the organization level — this is needed to
  set up the Pingala Process template and the D365 F&O time-registration integration
- All Pingala consultants (both guest and ext_ accounts) must be added as **team members**
  with **Basic** licence level in the DevOps project

> **Note:** Project Collection Administrator rights are scoped to projects the user has access
> to — they do not grant visibility into other projects in the customer's DevOps organization.
> This is a permanent right for the duration of the engagement.

---

## 2 — Guest User Accounts (Pingala identities)

Pingala consultants are invited as **guest users** into the customer's Entra ID using their
Pingala email addresses. These accounts are used primarily for Azure DevOps access and carry
their own licences from the Pingala tenant.

**Standard set of guest users per project:**

| Role | Typical Pingala identity | Purpose |
|------|--------------------------|---------|
| Solution Architect / Lead | e.g. `wparker@pingala.eu` | DevOps, architecture |
| Senior Consultant | e.g. `sgath@pingala.eu` | Fabric development |
| Consultant | e.g. `mknutzon@pingala.eu` | Fabric development |
| Consultant | e.g. `okoeltzsch@pingala.eu` | Fabric development |
| DevOps / Integration resource | e.g. `dviljoen@pingala.eu` | DevOps setup, D365 F&O integration |

The number of consultants varies per project — typically 3–5 delivering consultants plus 1
DevOps/integration resource.

**What to request from the customer:**

- Invite each Pingala consultant as a guest user using their `@pingala.eu` address
- The DevOps/integration resource needs Project Collection Administrator rights (see section 1)

---

## 3 — External User Accounts (Customer Tenant)

For work in Power BI / Fabric, Pingala consultants need **local accounts** in the customer's
Entra ID tenant (not guest accounts). These are typically prefixed `ext_` and follow the
customer's naming convention for external users.

**Standard set of ext_ accounts per project:**

One ext_ account per delivering consultant. Example naming:

| Consultant | Example ext_ account |
|------------|----------------------|
| Simon Reinholdt Gath | `ext_sigr@customer.dk` |
| Mads Knutzon | `ext_makn@customer.dk` |
| Oliver Koeltzsch | `ext_olko@customer.dk` |
| William Parker | `ext_wipa@customer.dk` |

The exact naming follows the customer's standard — Pingala does not dictate the format.

**What to request from the customer:**

- Create one ext_ (external user) account per delivering Pingala consultant
- The names can follow any convention the customer uses for external users
- These accounts will receive all Entra ID group memberships and Fabric workspace roles

---

## 4 — Service Principal (App Registration)

A service principal is used to drive Fabric data flows and connections to data stores so that
the solution is not dependent on individual user accounts.

**What to request from the customer:**

- Create an **App Registration** in Entra ID for the Fabric project
- **Redirect URI**: `https://app.powerbi.com`
- **API Permissions**:
  - `PowerBI Service / Item.Execute.All`
  - `PowerBI Service / Item.ReadWrite.All`
- Create a corresponding **Entra ID security group** for the service principal (see section 7)
  — this group is used to grant the service principal access in the Fabric Admin Portal

> **Naming convention for the service principal group:** `SG-Fabric-ServicePrincipals` or
> similar (e.g. `Fabric_ServicePrincipals`). The group should contain the service principal's
> object and optionally any future service principals for the same project.

---

## 5 — Azure Key Vault

The service principal's client secret is stored in an Azure Key Vault so that when the secret
expires, it can be rotated in one place instead of updating every Fabric connection individually.

**What to request from the customer:**

- Create an Azure Key Vault for the project (or designate an existing one)
- Store the service principal's **client secret** as a secret in the Key Vault
- Grant the Pingala delivering consultants (ext_ accounts) **Key Vault Administrator** or
  at minimum **Key Vault Secrets User** access, so they can reference the secret from Fabric
- Fabric is then configured to point to the Key Vault, and the secret is used for
  authentication in all connections

> **How it works:** Fabric references the Key Vault. When a connection needs to authenticate,
> it reads the service principal's secret from the Key Vault. When the secret expires, a new
> one is created and only the Key Vault secret value needs updating — all connections
> automatically pick up the new value.

---

## 6 — Licences

Guest users (Pingala identities) bring their own licences. The customer only needs to assign
licences to the **ext_ accounts**.

**Standard licence matrix:**

| Role | Power BI | Power Apps | DevOps |
|------|----------|------------|--------|
| Solution Architect / Lead | Pro | Power Apps Developer (free) | Basic |
| Senior Consultant | Pro | — | Basic |
| Consultant | Pro | — | Basic |

- **Pro** is sufficient for all roles — workspaces run on the Fabric capacity, which provides
  the premium features, so Premium Per User (PPU) is not required
- **Power Apps Developer** (free licence) is needed if the lead will work with Power Platform /
  D365 F&O environments
- **DevOps Basic** is needed for all ext_ accounts that will access Azure DevOps

**What to request from the customer:**

- Assign the licences above to each ext_ account based on their role

---

## 7 — Entra ID Security Groups

The following security groups should be created in the customer's Entra ID. They are used to
manage Fabric workspace roles, admin portal settings, and capacity administration in a
structured, scalable way.

### 7.1 Tenant & Capacity Administration

| Group name | Purpose | Recommended members |
|------------|---------|---------------------|
| `SG-Fabric-Tenant-Admin` | Fabric tenant administrator | Pingala solution architect + selected customer stakeholders |
| `SG-Fabric-Capacity-Admin` | Fabric capacity administrator | All Pingala consultants (ext_ accounts) |

### 7.2 Landing Zone Workspace Groups

| Group name | Purpose | Recommended members |
|------------|---------|---------------------|
| `SG-Fabric-LandingZone-Admin` | Admin on landing zone dev, test & prod workspaces | Pingala solution architect |
| `SG-Fabric-LandingZone-Member` | Member on landing zone dev, test & prod workspaces | All Pingala consultants |
| `SG-Fabric-LandingZone-Contributor` | Contributor on landing zone dev & test workspaces | Customer's own resources |

### 7.3 ETL Workspace Groups

| Group name | Purpose | Recommended members |
|------------|---------|---------------------|
| `SG-Fabric-ETL-Admin` | Admin on ETL dev, test & prod workspaces | Pingala solution architect |
| `SG-Fabric-ETL-Member` | Member on ETL dev, test & prod workspaces | All Pingala consultants |
| `SG-Fabric-ETL-Contributor` | Contributor on ETL dev & test workspaces | Customer's own resources |

### 7.4 Data Service Workspace Groups

| Group name | Purpose | Recommended members |
|------------|---------|---------------------|
| `SG-Fabric-DataService-Admin` | Admin on data service dev, test & prod workspaces | Pingala solution architect |
| `SG-Fabric-DataService-Member` | Member on data service dev, test & prod workspaces | All Pingala consultants |
| `SG-Fabric-DataService-Contributor` | Contributor on data service dev & test workspaces | Customer's own resources |
| `SG-Fabric-DataService-APP-Viewer` | App viewers who consume published Power BI apps | End users at the customer |

### 7.5 Service Principal Group

| Group name | Purpose | Recommended members |
|------------|---------|---------------------|
| `SG-Fabric-ServicePrincipals` | Grant service principal(s) access via Fabric Admin Portal | The project's service principal |

> **Pattern:** Each workspace layer (LandingZone, ETL, DataService) follows the same
> Admin / Member / Contributor pattern. Admin and Member groups span all three environments
> (dev, test, prod). Contributor groups span only dev and test — contributors do not get
> direct access to production.

---

## 8 — Role & Permission Assignments

Once users, groups, and the service principal are in place, the following permissions must be
configured.

### 8.1 Fabric Admin Portal Settings

These settings are configured in the **Fabric Admin Portal** (admin.powerbi.com) and control
tenant-wide capabilities:

- **Allow service principals to use Fabric APIs** — enable for the `SG-Fabric-ServicePrincipals`
  security group
- **Allow users to create workspaces** — enable for ext_ accounts (or the relevant security
  groups)

> Pingala's solution architect can assist the customer with configuring these settings.

### 8.2 Workspace Role Assignments

Each Fabric workspace is assigned roles using the Entra ID security groups from section 7:

| Workspace | Admin group | Member group | Contributor group |
|-----------|-------------|-------------|-------------------|
| LandingZone-DEV | SG-Fabric-LandingZone-Admin | SG-Fabric-LandingZone-Member | SG-Fabric-LandingZone-Contributor |
| LandingZone-TEST | SG-Fabric-LandingZone-Admin | SG-Fabric-LandingZone-Member | SG-Fabric-LandingZone-Contributor |
| LandingZone-PROD | SG-Fabric-LandingZone-Admin | SG-Fabric-LandingZone-Member | — |
| ETL-DEV | SG-Fabric-ETL-Admin | SG-Fabric-ETL-Member | SG-Fabric-ETL-Contributor |
| ETL-TEST | SG-Fabric-ETL-Admin | SG-Fabric-ETL-Member | SG-Fabric-ETL-Contributor |
| ETL-PROD | SG-Fabric-ETL-Admin | SG-Fabric-ETL-Member | — |
| DataService-DEV | SG-Fabric-DataService-Admin | SG-Fabric-DataService-Member | SG-Fabric-DataService-Contributor |
| DataService-TEST | SG-Fabric-DataService-Admin | SG-Fabric-DataService-Member | SG-Fabric-DataService-Contributor |
| DataService-PROD | SG-Fabric-DataService-Admin | SG-Fabric-DataService-Member | — |

> **CI/CD requires Admin.** Configuring Git integration and deployment pipelines on a
> workspace requires the **Workspace Admin** role — Member/Contributor cannot connect
> the workspace to Git or create/assign deployment pipelines. Ensure whoever sets up
> CI/CD is in the relevant `-Admin` group, not just `-Member`. The default model
> reserves Admin for the solution architect; on smaller engagements where the
> delivering consultant sets up CI/CD, that consultant needs Admin too.

### 8.3 Power Platform Roles (if applicable)

If the project involves D365 Finance & Operations integration:

- The lead Pingala consultant (ext_ account) needs the **SysAdmin** role on the D365 F&O
  environment linked to the customer's Power Platform

### 8.4 DevOps Roles

- All users (both guest and ext_ accounts) → **Team Member** on the project
- DevOps/integration resource (guest account) → **Project Collection Administrator** at org level

---

## Using This Skill — Generating an Access Request

When a user asks to draft an access request for a new customer, follow this workflow:

### Step 1: Collect project details

Ask for (if not already known):

- **Customer name**
- **Names and email addresses of the Pingala consultants** who will deliver
- **Name and email of the DevOps/integration resource**
- **Which consultant is the solution architect / lead?**
- **Does the project involve D365 F&O integration?** (determines Power Platform roles)

### Step 2: Generate the personalised access request

Using the template above, substitute the actual consultant names and email addresses into
each section. Present the full access request as a structured document or email that can be
sent to the customer's IT department.

### Step 3: Track completion

Present a checklist the user can track:

- [ ] Azure DevOps project created
- [ ] Guest users invited (Pingala identities)
- [ ] External user accounts created (ext_ accounts)
- [ ] Service Principal created with correct API permissions
- [ ] Azure Key Vault created with service principal secret
- [ ] Key Vault access granted to ext_ accounts
- [ ] Licences assigned to ext_ accounts
- [ ] Entra ID security groups created (all 12 groups)
- [ ] Ext_ accounts added to appropriate security groups
- [ ] Service principal added to SG-Fabric-ServicePrincipals
- [ ] Fabric Admin Portal settings configured
- [ ] Workspace roles assigned via security groups
- [ ] DevOps/integration resource granted Project Collection Administrator
- [ ] Power Platform SysAdmin assigned (if applicable)

---

## Quick Reference — What the Customer Must Do vs What Pingala Does

| Action | Responsible |
|--------|-------------|
| Create ext_ user accounts | Customer IT |
| Invite guest users | Customer IT |
| Create App Registration (service principal) | Customer IT |
| Create Azure Key Vault and store secret | Customer IT |
| Create Entra ID security groups | Customer IT |
| Assign licences to ext_ accounts | Customer IT |
| Grant Project Collection Admin to DevOps resource | Customer IT |
| Configure Fabric Admin Portal settings | Pingala (with customer approval) |
| Assign workspace roles via security groups | Pingala |
| Set up Azure DevOps project and process template | Pingala (DevOps resource) |
| Configure Key Vault reference in Fabric | Pingala |
