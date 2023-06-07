class LifecycleAware:
    """
    A class inheriting from this one indicates it has awareness for lifecycle. 'Setup' and 'cleanup' callbacks
    will be invoked during construction/tear-down phases.
    """

    def setup(self):
        """
        Called during the setup phase of the pipeline.
        """
        pass

    def cleanup(self):
        """
        Called during the tear-down process of the pipeline.
        """
        pass
