from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

class ProgressBarManager:
    """
    A class that manages the progress bar for tasks.

    Args:
        console (Console): The console object used for displaying the progress bar.

    Attributes:
        console (Console): The console object used for displaying the progress bar.
        progress (Progress): The progress bar object.

    Methods:
        start_progress: Starts a new task and returns its task ID.
        update_progress: Updates the progress of a task.
        complete_progress: Completes a task and updates its progress to 100%.
    """

    def __init__(self, console):
        self.console = console
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        )

    def start_progress(self, description):
        
        return self.progress.add_task(description, total=100)

    def update_progress(self, task_id, advance, description):
        
        self.progress.update(task_id, advance=advance, description=description)

    def complete_progress(self, task_id, description):
        
        self.progress.update(task_id, completed=100, description=description)

    def __enter__(self):
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()