class Signal:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Signal, cls).__new__(cls)
            cls._instance.listeners = {}
        return cls._instance

    def subscribe(self, event_name: str, listener: callable):
        self.listeners.setdefault(event_name, []).append(listener)

    def unsubscribe(self, listener):
        for event_name, listeners in self.listeners.items():
            if listener in listeners:
                listeners.remove(listener)

    def emit(self, event_name: str, *args, **kwargs):
        for listener in self.listeners.get(event_name, []):
            listener(*args, **kwargs)


def subscribe(event_name: str, listener: callable):
    signal = Signal()
    signal.subscribe(event_name, listener)


def unsubscribe(listener):
    signal = Signal()
    signal.unsubscribe(listener)


def emit(event_name: str, *args, **kwargs):
    signal = Signal()
    signal.emit(event_name, *args, **kwargs)
