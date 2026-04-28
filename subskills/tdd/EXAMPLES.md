# TDD Examples

Worked examples of the Harness TDD workflow for common scenarios.

## Example 1: Domain Entity (Go)

### RED Cycle

**Role:** TDD-RED
**Files:** `tests/unit/order_test.go` (create)

```go
package unit_test

import (
    "testing"
    "github.com/stretchr/testify/require"
    "myapp/src/ordering/domain"
)

func TestOrder_Create_SetsInitialStatus(t *testing.T) {
    order := domain.NewOrder("cust-123")
    require.Equal(t, domain.StatusDraft, order.Status())
}

func TestOrder_AddItem_IncrementsLineCount(t *testing.T) {
    order := domain.NewOrder("cust-123")
    order.AddItem(domain.Item{SKU: "WIDGET-01", Qty: 2, Price: 9.99})
    require.Len(t, order.Lines(), 1)
    require.Equal(t, 19.98, order.Total())
}

func TestOrder_Submit_WithEmptyItems_ReturnsError(t *testing.T) {
    order := domain.NewOrder("cust-123")
    err := order.Submit()
    require.ErrorIs(t, err, domain.ErrEmptyOrder)
}

func TestOrder_Submit_SetsStatusToPending(t *testing.T) {
    order := domain.NewOrder("cust-123")
    order.AddItem(domain.Item{SKU: "WIDGET-01", Qty: 1, Price: 10.00})
    err := order.Submit()
    require.NoError(t, err)
    require.Equal(t, domain.StatusPending, order.Status())
}
```

**Verify:** Tests fail (domain.Order doesn't exist yet).
**Commit:** `RED: order creation, item addition, and submission`

### GREEN Cycle

**Role:** TDD-GREEN
**Files:** `src/ordering/domain/order.go` (create)

```go
package domain

import "errors"

type Status int

const (
    StatusDraft Status = iota
    StatusPending
)

var ErrEmptyOrder = errors.New("cannot submit empty order")

type Line struct {
    SKU   string
    Qty   int
    Price float64
}

type Order struct {
    customerID string
    status     Status
    lines      []Line
}

func NewOrder(customerID string) *Order {
    return &Order{customerID: customerID, status: StatusDraft}
}

func (o *Order) Status() Status          { return o.status }
func (o *Order) Lines() []Line           { return o.lines }
func (o *Order) CustomerID() string      { return o.customerID }

func (o *Order) AddItem(item Item) {
    o.lines = append(o.lines, Line{SKU: item.SKU, Qty: item.Qty, Price: item.Price})
}

func (o *Order) Total() float64 {
    var total float64
    for _, l := range o.lines {
        total += float64(l.Qty) * l.Price
    }
    return total
}

func (o *Order) Submit() error {
    if len(o.lines) == 0 {
        return ErrEmptyOrder
    }
    o.status = StatusPending
    return nil
}
```

**Verify:** All RED tests pass.
**Commit:** `GREEN: order entity with create, add item, submit`

### REFACTOR Cycle

**Role:** TDD-REFACTOR
**Files:** `src/ordering/domain/order.go` (modify)

```go
// Refactored: extracted total calculation, used named return
func (o *Order) Total() (total float64) {
    for _, l := range o.lines {
        total += float64(l.Qty) * l.Price
    }
    return total
}

// Refactored: added validation method for clarity
func (o *Order) canSubmit() error {
    if len(o.lines) == 0 {
        return ErrEmptyOrder
    }
    return nil
}

func (o *Order) Submit() error {
    if err := o.canSubmit(); err != nil {
        return err
    }
    o.status = StatusPending
    return nil
}
```

**Verify:** Tests still pass (no test files touched).
**Commit:** `REFACTOR: extract validation, clean up total calculation`

### REVIEWER Cycle

**Role:** REVIEWER
**Files:** `specs/001-order-management/report.md` (create)

```markdown
# TDD Report: Order Entity

## Compliance
- [x] All RED tests pass
- [x] No implementation modified during RED
- [x] No tests modified during GREEN
- [x] No tests modified during REFACTOR
- [x] No speculative features added

## Spec Alignment
- US1 (Create Order): ✅ Covered by RED tests
- Acceptance criteria AC-001: ✅ Empty order rejection
- Acceptance criteria AC-002: ✅ Status transition

## `harness verify-ai` Results
```
$ harness verify-ai --role TDD-RED --base HEAD~4
PASS: Only test and spec files modified
$ harness verify-ai --role TDD-GREEN --base HEAD~3
PASS: No test files modified
$ harness verify-ai --role TDD-REFACTOR --base HEAD~1
PASS: No test files modified, no new public symbols
$ harness verify-ai --role REVIEWER
PASS: Report only, no source modifications
```
```

---

## Example 2: HTTP Handler (Python)

### RED Cycle

**Role:** TDD-RED
**Files:** `tests/test_create_order_handler.py` (create)

```python
import pytest
from http import HTTPStatus

def test_create_order_returns_201_with_valid_payload(client, valid_order_payload):
    response = client.post("/orders", json=valid_order_payload)
    assert response.status_code == HTTPStatus.CREATED
    assert "order_id" in response.json

def test_create_order_returns_422_with_empty_items(client):
    response = client.post("/orders", json={"customer_id": "cust-123", "items": []})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

def test_create_order_returns_400_with_missing_customer(client, valid_order_payload):
    del valid_order_payload["customer_id"]
    response = client.post("/orders", json=valid_order_payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
```

**Commit:** `RED: create order HTTP handler acceptance tests`

### GREEN Cycle

**Role:** TDD-GREEN
**Files:** `src/ordering/handlers/create_order.py` (create)

```python
from http import HTTPStatus
from flask import request, jsonify

def create_order(order_service):
    data = request.get_json()
    if not data or "customer_id" not in data:
        return jsonify({"error": "customer_id required"}), HTTPStatus.BAD_REQUEST
    if not data.get("items"):
        return jsonify({"error": "items cannot be empty"}), HTTPStatus.UNPROCESSABLE_ENTITY

    order = order_service.create(data["customer_id"], data["items"])
    return jsonify({"order_id": order.id}), HTTPStatus.CREATED
```

**Commit:** `GREEN: create order handler with validation`

---

## Example 3: Boundary Violation (What NOT To Do)

### Violation: RED Agent Writes Implementation

```bash
$ harness verify-ai --role TDD-RED --base HEAD~1
ERROR: Role boundary violation
  Role: TDD-RED
  Forbidden files modified:
    - src/ordering/domain/order.go (implementation not allowed for TDD-RED)
  Fix: Move implementation to a GREEN-cycle commit
```

### Violation: GREEN Agent Modifies Tests

```bash
$ harness verify-ai --role TDD-GREEN --base HEAD~1
ERROR: Role boundary violation
  Role: TDD-GREEN
  Forbidden files modified:
    - tests/unit/order_test.go (test files not allowed for TDD-GREEN)
  Fix: Revert test changes, run RED cycle if tests need updating
```
