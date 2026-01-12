"""
Tool context and binding utilities.

Provides decorators and context objects for binding external objects
(agents, API clients, etc.) to tool functions without using closures.
"""

import types
from typing import Any, Callable, Dict, Optional


class ToolContext:
    """
    Context object holding shared resources for tools.
    
    Stores objects (agents, API clients, databases, etc.) that tools need access to.
    
    Args:
        **objects: Named objects to store in the context.
        
    Example:
        >>> ctx = ToolContext(agent=my_agent, gmail=gmail_client)
        >>> ctx.agent.memorize("something")
        >>> ctx.gmail.send(to="user@example.com", subject="Hi")
    """
    
    def __init__(self, **objects: Any):
        """
        Initialize context with named objects.
        
        Args:
            **objects: Named objects to store (e.g., agent=my_agent, db=database).
        """
        # Store object names explicitly to avoid issues with dir()
        # dir() would return ALL attributes including methods/properties from subclasses,
        # which we don't want to inject into function globals
        self._object_names = set(objects.keys())
        for name, obj in objects.items():
            setattr(self, name, obj)
    
    def __repr__(self) -> str:
        """String representation showing available objects."""
        # Use stored _object_names instead of dir() to only show bound objects,
        # not methods or properties
        return f"ToolContext({', '.join(sorted(self._object_names))})"


def bind(
    *,
    context: Optional[ToolContext] = None,
    **bound_objects: Any
) -> Callable:
    """
    Decorator that binds objects to a function without them appearing in the signature.
    
    Can be used in three ways:
    1. Pass a ToolContext instance: @bind(context=ctx)
    2. Pass objects directly: @bind(agent=my_agent, gmail=gmail_client)
    3. Combine both: @bind(context=ctx, extra_obj=something)
    
    When combining ToolContext with additional kwargs, the kwargs take precedence
    if there are naming conflicts.
    
    **WARNING: Global Namespace Injection**
    This decorator injects bound objects into the function's global namespace.
    This means:
    - Bound objects can override existing global variables with the same name
    - Name conflicts can cause hard-to-debug issues
    - Choose unique names for bound objects to avoid conflicts
    
    Args:
        context: Optional ToolContext instance containing objects to bind.
        **bound_objects: Additional objects to bind (when not using ToolContext,
                        or to add/override objects from ToolContext).
        
    Returns:
        Decorated function with objects bound.
        
    Example with ToolContext:
        >>> ctx = ToolContext(agent=my_agent, gmail=gmail_client)
        >>> @bind(context=ctx)
        ... def send_email(to: str, subject: str):
        ...     gmail.send(to=to, subject=subject)
        ...     agent.memorize(f"Sent email to {to}")
        
    Example with direct objects:
        >>> @bind(agent=my_agent, gmail=gmail_client)
        ... def send_email(to: str, subject: str):
        ...     gmail.send(to=to, subject=subject)
        ...     agent.memorize(f"Sent email to {to}")
        
    Example combining both:
        >>> ctx = ToolContext(agent=my_agent, gmail=gmail_client)
        >>> @bind(context=ctx, db=database)
        ... def send_and_log(to: str):
        ...     gmail.send(to=to, subject="Hi")
        ...     db.log(f"Sent to {to}")
        ...     agent.memorize(f"Sent to {to}")
    """
    # Handle both calling styles: @bind(ctx) and @bind(agent=..., gmail=...)
    if context is None:
        # Called as @bind(agent=x, gmail=y)
        objects_to_bind = bound_objects
    elif isinstance(context, ToolContext):
        # Called as @bind(context=ctx) or @bind(context=ctx, extra_obj=...)
        # Extract objects from context using stored names (not dir())
        # This ensures we only get the objects passed to __init__, not methods/properties
        objects_to_bind = {
            key: getattr(context, key)
            for key in context._object_names
        }
        # Merge additional bound_objects (they take precedence over context objects)
        objects_to_bind.update(bound_objects)
    else:
        # Called as @bind(something) where something is not a ToolContext
        # This shouldn't happen with proper usage, but handle gracefully
        raise TypeError(
            f"bind() expects either a ToolContext instance or keyword arguments, "
            f"got {type(context).__name__}"
        )
    
    def decorator(func: Callable) -> Callable:
        """Inner decorator that wraps the function."""
        # Inject bound objects into function's global namespace
        # Python's name resolution: Local -> Enclosing -> Global -> Built-in
        # Since we can't modify Local or Enclosing scopes after function definition,
        # we inject into Global scope so the function can access bound objects
        new_globals = func.__globals__.copy()
        new_globals.update(objects_to_bind)
        
        # Create a new function with the updated globals
        # We use types.FunctionType to create a new function object that:
        # - Uses the same bytecode (func.__code__)
        # - Has bound objects in its globals (new_globals)
        # - Preserves defaults, closure, and other function properties
        new_func = types.FunctionType(
            func.__code__,      # Same bytecode
            new_globals,        # Updated globals with bound objects
            func.__name__,      # Same name
            func.__defaults__,  # Same default arguments
            func.__closure__    # Same closure (important for nested functions)
        )
        
        # Copy function metadata for introspection and debugging
        new_func.__dict__.update(func.__dict__)
        new_func.__doc__ = func.__doc__
        new_func.__annotations__ = func.__annotations__
        new_func.__module__ = func.__module__
        new_func.__qualname__ = func.__qualname__
        
        # Store bound objects as function attribute for introspection
        # This allows tools like get_bound_objects() to retrieve them
        new_func._bound_objects = objects_to_bind
        
        return new_func
    
    return decorator


def get_bound_objects(func: Callable) -> Dict[str, Any]:
    """
    Get objects bound to a function via @bind decorator.
    
    Args:
        func: Function to inspect.
        
    Returns:
        Dictionary of bound object names to objects. Empty dict if none bound.
        
    Example:
        >>> @bind(agent=my_agent)
        ... def tool(x: int, agent):
        ...     return x
        >>> get_bound_objects(tool)
        {'agent': <Agent instance>}
    """
    return getattr(func, '_bound_objects', {})

