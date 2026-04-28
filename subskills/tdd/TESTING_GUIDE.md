# Testing Guide

Philosophy and patterns for writing tests in the Harness TDD workflow.

## Core Philosophy

Tests verify **behavior through public interfaces**, not implementation details. A good test:

1. Describes what the system does, not how it does it
2. Uses the public API or interface — never reaches into internals
3. Would survive a complete rewrite of the implementation
4. Fails for exactly one reason
5. Has a name that reads like a requirement

## Test Categories

### Unit Tests

Test a single unit in isolation. Mock or stub external dependencies.

```
File: tests/unit/order_test.go
Pattern: func Test{Behavior}(t *testing.T)
```

### Integration Tests

Test multiple units working together. Use real dependencies where possible (in-memory DB, test server).

```
File: tests/integration/create_order_test.go
Pattern: func Test{Feature}_{Scenario}(t *testing.T)
```

### Acceptance Tests

Test against the spec's acceptance criteria. These are the tests that RED writes first.

```
File: tests/acceptance/order_lifecycle_test.go
Pattern: Maps directly to spec.md acceptance criteria IDs
```

## Naming Conventions

```go
// ✅ Good: describes behavior
func TestOrder_Submit_SetsStatusToPending(t *testing.T)

// ✅ Good: describes edge case
func TestOrder_Submit_EmptyItems_ReturnsError(t *testing.T)

// ❌ Bad: describes implementation
func TestOrder_statusField_IsSet(t *testing.T)

// ❌ Bad: vague
func TestOrderWorks(t *testing.T)
```

```python
# ✅ Good
def test_submit_order_with_items_sets_status_to_pending():

# ❌ Bad
def test_order():
```

## Test Structure: Arrange-Act-Assert

```go
func TestOrder_Submit_SetsStatusToPending(t *testing.T) {
    // Arrange
    order := domain.NewOrder("cust-123")
    order.AddItem(domain.Item{SKU: "WIDGET", Qty: 2})

    // Act
    err := order.Submit()

    // Assert
    require.NoError(t, err)
    assert.Equal(t, domain.StatusPending, order.Status())
}
```

## Patterns

### Pattern: Test the Public Interface

```go
// ✅ Test through public methods
order := domain.NewOrder("cust-123")
order.AddItem(item)
err := order.Submit()

// ❌ Don't reach into internals
order := &domain.Order{CustomerID: "cust-123", status: 0}
```

### Pattern: One Assertion Per Concept

Multiple related assertions are fine. Unrelated assertions belong in separate tests.

```go
// ✅ All assertions relate to the same behavior
assert.Equal(t, domain.StatusPending, order.Status())
assert.Equal(t, time.Now().UTC().Round(time.Second), order.SubmittedAt().Round(time.Second))

// ❌ Mixing unrelated behaviors
assert.Equal(t, domain.StatusPending, order.Status())
assert.True(t, repo.WasCalled) // This is about the repo, not the order
```

### Pattern: Test Data Builders

For complex test setup, use builder functions:

```go
func validOrder() *domain.Order {
    o := domain.NewOrder("cust-123")
    o.AddItem(domain.Item{SKU: "WIDGET", Qty: 1})
    return o
}

func (o *domain.Order) withCustomerID(id string) *domain.Order {
    // use reflection or a test-only setter if needed
    return o
}
```

## Anti-Patterns

### Anti-Pattern: Testing Private Methods

If you need to test a private method, the public interface is wrong. Either:
1. Promote the method to public, or
2. Extract a new type with a public interface

### Anti-Pattern: Mocking What You Own

Mock external systems (databases, APIs). Don't mock your own domain objects — use the real ones.

### Anti-Pattern: Speculative Tests

Don't write tests for behavior the spec doesn't require. The RED cycle writes tests for spec requirements, not imagined edge cases.

### Anti-Pattern: Overspecified Tests

Tests that break when implementation changes (but behavior doesn't) are overspecified. They test the "how" not the "what."

## Refactoring Safety

During the REFACTOR cycle:

1. Tests must not change — they are the safety net
2. If a refactor requires test changes, the refactor is wrong (it changed behavior) or the test was overspecified
3. Run tests after every refactor step
4. If tests break, revert the refactor, not the tests
