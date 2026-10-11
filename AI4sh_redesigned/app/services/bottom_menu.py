# Bottom-panel activity registration and selection. Numeric IDs are local to this menu;
# string activity IDs are shared across the runtime registry and must be globally unique.
from .workspace_context import services
from ..activities.activity_base import Activity

class BottomMenu:
    @staticmethod
    # Accept an imported Activity subclass, instantiate it, and register its metadata.
    # Duplicate numeric menu IDs or globally registered activity IDs are rejected.
    def add(id, text, activity, icon, enabled=True):
        if not isinstance(id, int):
            raise ValueError("Menu ID must be an integer")
        if not isinstance(activity, type) or not issubclass(activity, Activity):
            raise ValueError("Pass an imported Activity class")
        s = services()
        with s.lock:
            if id in s.bottom_menu:
                raise ValueError(f"Menu ID {id} already exists")
            item = activity()
            if item.id in s.registry:
                raise ValueError(f"Activity {item.id} already exists")
            item.definition.title, item.definition.icon, item.definition.enabled = text, icon, enabled
            item.definition.placement = "bottom"
            s.registry[item.id] = item
            s.bottom_menu[id] = item.id

    @staticmethod
    # Remove both the menu mapping and activity registry entry; missing IDs are harmless.
    def remove(id):
        s = services()
        with s.lock:
            activity_id = s.bottom_menu.pop(id, None)
            if activity_id:
                s.registry.pop(activity_id, None)

    @staticmethod
    # Enable a registered entry and clear its previous disabled reason.
    def enable(id):
        s = services()
        with s.lock:
            item = s.registry[s.bottom_menu[id]]
            item.definition.enabled, item.definition.reason = True, ""

    @staticmethod
    # Keep the entry registered but prevent selection, with a reason for the UI.
    def disable(id, reason="Disabled"):
        s = services()
        with s.lock:
            item = s.registry[s.bottom_menu[id]]
            item.definition.enabled, item.definition.reason = False, reason

    @staticmethod
    # Check membership in the bottom-menu numeric ID namespace.
    def contains(id):
        s = services()
        with s.lock:
            return id in s.bottom_menu

    @staticmethod
    # Select and reload an enabled bottom activity. This does not reveal a closed panel;
    # call BottomPanel.open() separately when visibility should change.
    def open(id):
        s = services()
        with s.lock:
            item = s.registry[s.bottom_menu[id]]
            if not item.enabled:
                raise ValueError("Activity is disabled")
            s.command("bottom.open", item.id)
            s.command("bottom.reload", item.id)
