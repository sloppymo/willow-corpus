# Enhanced Dataset Schema Documentation

*Generated on: 2025-06-29 15:01:49*

## Overview

This document describes the schema for the enhanced dataset containing 3 scenarios.

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scenario_id` | `str` | Yes | No description available |
| `title` | `str` | Yes | No description available |
| `description` | `str` | Yes | No description available |
| `vulnerabilities` | `list` | Yes | No description available |
| `scenario` | `str` | Yes | No description available |
| `responses` | `list` | Yes | No description available |
| `metadata` | `dict` | Yes | No description available |
| `messages` | `list` | Yes | No description available |

## Vulnerabilities

The following vulnerability types are used in the dataset:

- `another_vulnerability`
- `communication_breakdown`
- `interpersonal_conflict`
- `other_vulnerability`

## Message Roles

The following message roles are used in the dataset:

- `tenant1`
- `tenant2`

## Emotional States

The following emotional states are used in the dataset:

- `defensive`
- `frustrated`

## Validation Statuses

The following validation statuses are used in the dataset:

- `pending_review`
- `validated`

## Example Scenario

```json
{
  "scenario_id": "example_id",
  "title": "Example Scenario",
  "description": "Example scenario description",
  "vulnerabilities": [
    "example_vulnerability"
  ],
  "messages": [
    {
      "role": "tenant",
      "content": "Example message",
      "emotional_state": "neutral"
    }
  ],
  "metadata": {
    "created_at": "2025-01-01T00:00:00Z",
    "last_updated": "2025-01-01T00:00:00Z",
    "validation_status": "validated"
  }
}
```