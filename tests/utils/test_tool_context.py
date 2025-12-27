"""
Tests for ToolContext and bind decorator.

Verifies that objects can be bound to tool functions using either
ToolContext instances or direct keyword arguments.

IMPORTANT RULES FOR @bind DECORATOR TESTS:
1. Bound objects are AUTOMATICALLY INJECTED by the decorator into the function's global scope
2. Bound objects should NOT appear in function signatures
3. Local variables must have DIFFERENT names than bound object keys
   Example: storage_obj = SimpleStorage(), then @bind(storage=storage_obj)
4. Inside decorated functions, use the bound object names directly (storage, email, etc.)
   These are injected by the decorator into globals, NOT passed as parameters

CORRECT:
    storage_obj = SimpleStorage()
    @bind(storage=storage_obj)
    def my_func(x: int):
        storage.store(x)  # 'storage' is found in globals

WRONG:
    storage = SimpleStorage()
    @bind(storage=storage)
    def my_func(x: int, storage):  # ❌ Don't put storage in signature!
        storage.store(x)
"""

from ixmachina.utils import ToolContext, bind, get_bound_objects


class SimpleStorage:
    """Simple storage class for testing."""
    def __init__(self):
        self.data = []
    
    def store(self, text: str):
        """Store text."""
        self.data.append(text)
        return text


class EmailClient:
    """Simple email client for testing."""
    def __init__(self):
        self.sent = []
    
    def send(self, to: str, subject: str, body: str = ""):
        """Send an email."""
        email = {"to": to, "subject": subject, "body": body}
        self.sent.append(email)
        return email


def test_tool_context_creation():
    """Test creating a ToolContext with objects."""
    storage = SimpleStorage()
    email = EmailClient()
    
    ctx = ToolContext(storage=storage, email=email)
    
    assert ctx.storage is storage
    assert ctx.email is email


def test_tool_context_repr():
    """Test ToolContext string representation."""
    storage = SimpleStorage()
    email = EmailClient()
    
    ctx = ToolContext(storage=storage, email=email)
    repr_str = repr(ctx)
    
    assert "ToolContext" in repr_str
    assert "storage" in repr_str
    assert "email" in repr_str


def test_bind_with_tool_context():
    """Test @bind decorator with ToolContext."""
    storage1 = SimpleStorage()
    email1 = EmailClient() # checking to see if using a different name for email and storage variable works
    ctx = ToolContext(storage=storage1, email=email1)
    
    @bind(context=ctx)
    def send_and_store(to: str, subject: str):
        """Send an email and store the action."""
        result = email.send(to=to, subject=subject, body="Test")
        storage.store(f"Sent to {to}")
        return result
    
    # Call without passing storage/email
    result = send_and_store(to="user@example.com", subject="Hello")
    
    assert result["to"] == "user@example.com"
    assert result["subject"] == "Hello"
    assert len(email1.sent) == 1
    assert storage1.data[0] == "Sent to user@example.com"


def test_bind_with_direct_objects():
    """Test @bind decorator with direct keyword arguments."""
    storage_obj = SimpleStorage()
    email_obj = EmailClient()

    @bind(storage=storage_obj, email=email_obj)
    def send_and_store(to: str, subject: str):
        """Send an email and store the action."""
        result = email.send(to=to, subject=subject, body="Test")
        storage.store(f"Sent to {to}")
        return result
    
    # Call without passing storage/email
    result = send_and_store(to="user@example.com", subject="Hello")
    
    assert result["to"] == "user@example.com"
    assert result["subject"] == "Hello"
    assert len(email_obj.sent) == 1
    assert storage_obj.data[0] == "Sent to user@example.com"


def test_bind_with_regular_arguments():
    """Test that @bind works with regular function arguments."""
    storage_obj = SimpleStorage()
    
    @bind(storage=storage_obj)
    def add_and_store(x: int, y: int):
        """Add two numbers and store the result."""
        result = x + y
        storage.store(f"{x} + {y} = {result}")
        return result
    
    result = add_and_store(x=5, y=3)
    
    assert result == 8
    assert storage_obj.data[0] == "5 + 3 = 8"


def test_bind_kwargs_override():
    """Test that bound objects are accessible in the function."""
    storage_obj1 = SimpleStorage()
    
    @bind(storage=storage_obj1)
    def store_something(text: str):
        """Store text."""
        storage.store(text)
        return storage
    
    # Use bound storage
    result1 = store_something(text="test1")
    assert result1 is storage_obj1
    assert storage_obj1.data == ["test1"]
    
    # Use it again
    result2 = store_something(text="test2")
    assert result2 is storage_obj1
    assert storage_obj1.data == ["test1", "test2"]


def test_get_bound_objects():
    """Test retrieving bound objects from decorated function."""
    storage_obj = SimpleStorage()
    email_obj = EmailClient()
    
    @bind(storage=storage_obj, email=email_obj)
    def send_email(to: str):
        """Send an email."""
        pass
    
    bound = get_bound_objects(send_email)
    
    assert bound["storage"] is storage_obj
    assert bound["email"] is email_obj
    assert len(bound) == 2


def test_get_bound_objects_empty():
    """Test get_bound_objects on undecorated function."""
    def regular_function(x: int):
        """Regular function without @bind."""
        return x * 2
    
    bound = get_bound_objects(regular_function)
    
    assert bound == {}


def test_bind_preserves_function_name_and_docstring():
    """Test that @bind preserves function name and docstring."""
    storage_obj = SimpleStorage()
    
    @bind(storage=storage_obj)
    def my_tool(x: int):
        """This is my tool's docstring."""
        return x
    
    assert my_tool.__name__ == "my_tool"
    assert my_tool.__doc__ == "This is my tool's docstring."


def test_bind_with_multiple_objects():
    """Test @bind with many objects."""
    obj1 = SimpleStorage()
    obj2 = EmailClient()
    obj3 = {"key": "value"}
    obj4 = [1, 2, 3]
    obj5 = "string"
    
    @bind(a=obj1, b=obj2, c=obj3, d=obj4, e=obj5)
    def use_all():
        """Use all objects."""
        return [a, b, c, d, e]
    
    result = use_all()
    
    assert result[0] is obj1
    assert result[1] is obj2
    assert result[2] is obj3
    assert result[3] is obj4
    assert result[4] is obj5


def test_bind_invalid_type_raises_error():
    """Test that @bind raises TypeError for invalid input."""
    try:
        @bind("invalid_string")
        def tool(x: int):
            return x
        
        # Should not reach here
        assert False, "Expected TypeError"
    except TypeError as e:
        # The error should indicate that bind() doesn't accept positional arguments
        assert "positional arguments" in str(e)


def test_bind_context_with_additional_kwargs():
    """Test @bind with ToolContext plus additional keyword arguments."""
    storage_obj = SimpleStorage()
    email_obj = EmailClient()
    ctx = ToolContext(storage=storage_obj, email=email_obj)
    
    # Additional object not in context
    database = {"logs": []}
    
    @bind(context=ctx, db=database)
    def send_and_log(to: str, subject: str):
        """Send email, store, and log to database."""
        result = email.send(to=to, subject=subject)
        storage.store(f"Sent to {to}")
        db["logs"].append(f"Email sent to {to}")
        return result
    
    # Call without passing any bound objects
    result = send_and_log(to="user@example.com", subject="Hello")
    
    assert result["to"] == "user@example.com"
    assert len(email_obj.sent) == 1
    assert storage_obj.data[0] == "Sent to user@example.com"
    assert database["logs"][0] == "Email sent to user@example.com"


def test_bind_context_kwargs_override():
    """Test that additional kwargs override ToolContext objects."""
    storage_obj1 = SimpleStorage()
    storage_obj2 = SimpleStorage()
    email_obj = EmailClient()
    
    ctx = ToolContext(storage=storage_obj1, email=email_obj)
    
    # Override storage from context
    @bind(context=ctx, storage=storage_obj2)
    def send_email(to: str):
        """Send email with overridden storage."""
        result = email.send(to=to, subject="Test")
        storage.store(f"Sent to {to}")
        return result
    
    result = send_email(to="user@example.com")
    
    # Should use storage_obj2, not storage_obj1
    assert len(storage_obj2.data) == 1
    assert storage_obj2.data[0] == "Sent to user@example.com"
    assert len(storage_obj1.data) == 0
    assert len(email_obj.sent) == 1



