---
name: pingala-project-playbook
description: >
  The core playbook for how Pingala sets up and runs customer projects end-to-end.
  Use this skill whenever someone asks about project setup, onboarding a new customer project,
  the Pingala project process, how to kick off a project, or what steps are needed to get a
  project running. Also trigger when someone mentions any individual phase of the playbook —
  such as user provisioning, Entra ID setup, D365 F&O project creation, Azure DevOps project
  setup, backlog creation, sprint planning, Float capacity, or customer presentation — and
  needs to understand where that step fits in the overall process. This is the master reference
  that ties together all other Pingala skills (Azure DevOps Backlog, Entra ID groups, etc.).
  Use this skill even if the user only asks about one phase — it provides the full context
  of what comes before and after.
---

# Pingala Project Playbook

This is the master playbook for setting up and running a Pingala customer project. It defines
the standard sequence of phases every project goes through, from initial user provisioning to
the final customer presentation.

The playbook is a reference checklist — follow it phase by phase when onboarding a new project.
Several phases reference separate skills for detailed execution (e.g., the Azure DevOps Backlog
skill for backlog creation). Where a referenced skill does not yet exist, the playbook notes
this as a future dependency.

---

## Playbook overview

The project setup follows six phases in sequence. Each phase should be completed before moving
to the next.

```
Phase 1: Users & Access
Phase 2: Dynamics 365 F&O Project Management
Phase 3: Azure DevOps Setup
Phase 4: Azure DevOps Backlogs & Sprints
Phase 5: Float Capacity Planning
Phase 6: Presentation & Approval
```

---

## Phase 1 — Users & Access

This phase provisions all Pingala consultants in the customer's environment so they have the
access they need to deliver.

### 1.1 Create external users for delivering consultants

Create at least 4 Pingala consultants as **external users** in the customer's Entra ID tenant.
These are native accounts that live only in the customer's Entra ID (not guest accounts linked
to Pingala). These external user accounts are the ones that will receive all group memberships
and access rights in the customer environment.

### 1.2 Invite the same consultants as guest users

Invite the same 4 consultants as **guest users** using their Pingala identities into the
customer's Entra ID. This gives them a secondary presence linked to their home Pingala tenant.

### 1.3 Assign Entra ID groups and access rights

Using the **external user accounts** (from step 1.1, not the guest accounts), assign the 4
delivering consultants to the required Entra ID groups and grant the necessary access rights.

> **Dependency:** The specific list of Entra ID groups, service principal, Key Vault, licences,
> and their access rights is maintained in the `fabric-project-access` skill. Consult that skill
> for the exact group names, permissions, and the full access-request workflow.

### 1.4 Provision the DevOps/integration resource

In addition to the 4 delivering consultants, invite one additional Pingala resource as a
**guest user** (using their Pingala identity) in the customer's Entra ID. This person is
responsible for:

- Setting up the Azure DevOps project (Phase 3)
- Configuring the integration between Azure DevOps and Dynamics 365 F&O

This resource must be granted **Azure DevOps Project Collection Administrator** rights.

### Phase 1 checklist

- [ ] 4 external user accounts created in customer Entra ID
- [ ] 4 guest user invitations sent and accepted (Pingala identities)
- [ ] Entra ID groups and access rights assigned to external user accounts
- [ ] DevOps/integration resource invited as guest user
- [ ] DevOps/integration resource granted Project Collection Administrator rights

---

## Phase 2 — Dynamics 365 F&O Project Management

This phase sets up the financial tracking for the project in Pingala's internal D365 F&O.

### 2.1 Create the project

Create a new project in Pingala's internal Dynamics 365 F&O under the relevant customer.

### 2.2 Set up a fixed-price activity (if Atomic framework)

If the project involves sales of the Pingala Atomic framework on a fixed price:

1. Create a **fixed-price activity** within the project
2. Set the hourly rate of the fixed-price activity to the **same rate** as the rest of the
   project (so pricing is consistent across all activities)

### 2.3 Send an on-account invoice

Send an on-account invoice from the fixed-price activity created in step 2.2.

### 2.4 Distribute hours to the team

After the on-account invoice has been sent:

1. Take the invoiced amount and **divide it by the hourly rate** — this gives the total pool
   of available hours
2. The team draws down this pool by registering **"F" hours** on the specific fixed-price
   activity

This mechanism allows the fixed-price delivery to be tracked in hours against the invoiced
amount.

### Phase 2 checklist

- [ ] Project created in D365 F&O under the customer
- [ ] Fixed-price activity created (if Atomic framework, with matching hourly rate)
- [ ] On-account invoice sent from the fixed-price activity
- [ ] Hour pool calculated (invoiced amount ÷ hourly rate)
- [ ] Team informed about registering "F" hours on the activity

---

## Phase 3 — Azure DevOps Setup

This phase is performed by the DevOps/integration resource who was granted Project Collection
Administrator rights in Phase 1.

### 3.1 Set up the Pingala Process

Create the **Pingala Process** as a separate process template in the customer's Azure DevOps
organization. This is a prerequisite for creating the project — the Pingala Process defines
the work item types and workflow used in all Pingala projects.

### 3.2 Create the Azure DevOps project

Create a new Azure DevOps project using the Pingala Process established in step 3.1.

### 3.3 Set up and test the D365 F&O integration

Configure the integration between the new Azure DevOps project and Dynamics 365 F&O. Test
the integration to confirm that data flows correctly between the two systems before proceeding.

### Phase 3 checklist

- [ ] Pingala Process created as a process template in Azure DevOps
- [ ] New project created using the Pingala Process
- [ ] Azure DevOps ↔ D365 F&O integration configured
- [ ] Integration tested and confirmed working

---

## Phase 4 — Azure DevOps Backlogs & Sprints

This is the most involved phase. It takes the project from an empty Azure DevOps project to a
fully planned and estimated backlog with sprint assignments.

### 4.1 Create the backlog

Use the **Azure DevOps Backlog skill** (`azure-devops-backlog`) to generate and push the full
project backlog from the project brief. Follow that skill's workflow: extract details from the
brief, draft the backlog, review with the team, and push to Azure DevOps.

> **Dependency:** This step uses the `azure-devops-backlog` skill.

### 4.2 Estimate the backlog

Once the entire backlog has been created in Azure DevOps, the project team (the 4 delivering
consultants) goes through every work item and adds effort estimates. This is a collaborative
team exercise — all 4 consultants participate.

### 4.3 Set up sprints

Configure sprints within the Azure DevOps project:

- **Default sprint length:** 3 weeks
- Create enough sprints to cover the planned project duration

### 4.4 Set up sprint capacity

For each sprint, configure capacity for the 4 delivering consultants. This defines how many
hours each person is available per sprint.

### 4.5 Plan the backlog into sprints

With the backlog estimated, sprints created, and capacity set, plan the entire backlog into
sprints. Assign work items to specific sprints based on priority, dependencies, and available
capacity.

### Phase 4 checklist

- [ ] Full backlog created via the Azure DevOps Backlog skill
- [ ] All work items estimated by the 4-person project team
- [ ] Sprints configured (3-week cadence by default)
- [ ] Sprint capacity set for all 4 consultants
- [ ] Entire backlog planned into sprints

---

## Phase 5 — Float Capacity Planning

### 5.1 Update Float with capacity reservations

Once the Azure DevOps backlog has been planned into sprints with capacity, update Pingala's
**Float** resource management software to reflect the same capacity. For each resource (the 4
consultants), create capacity reservations in Float that correspond to their Azure DevOps
sprint capacity allocations.

The goal is to keep Float and Azure DevOps in sync so that Pingala's organization-wide
resource planning reflects the committed project capacity.

### Phase 5 checklist

- [ ] Float capacity reservations created for each of the 4 consultants
- [ ] Reservations match the Azure DevOps sprint capacity per resource
- [ ] Float reflects the full project timeline

---

## Phase 6 — Presentation & Approval

### 6.1 Export the backlog

Use an Azure DevOps query to export the entire backlog, including:

- All work items (Epics, Features, Work Packages, User Stories, Tasks)
- Effort estimates for each item
- Sprint assignments
- Capacity allocations

This export serves as the documentation for the customer presentation.

### 6.2 Present to the customer

Hold a meeting with the customer to present:

- The full backlog structure and scope
- The estimates for each area
- The sprint plan and timeline
- Resource allocation and capacity

### 6.3 Obtain approval

Document the customer's feedback and obtain approval of the backlog, estimates, and sprint
plan before delivery begins.

### Phase 6 checklist

- [ ] Backlog exported with estimates and sprint assignments
- [ ] Customer meeting scheduled and held
- [ ] Backlog, estimates, and plan presented
- [ ] Customer approval documented

---

## Quick reference — phase dependencies

| Phase | Depends on | Key skill / tool |
|-------|-----------|-----------------|
| 1. Users & Access | — | `fabric-project-access` skill |
| 2. D365 F&O Project | — | Dynamics 365 F&O |
| 3. Azure DevOps Setup | Phase 1 (DevOps resource needs access) | Azure DevOps |
| 4. Backlogs & Sprints | Phase 3 (project must exist) | `azure-devops-backlog` skill |
| 5. Float | Phase 4 (sprints must be planned) | Float |
| 6. Presentation | Phase 4 + 5 (need complete plan) | Azure DevOps queries |

Phases 1 and 2 can run in parallel since they have no mutual dependency. Phase 3 onward is
sequential.
