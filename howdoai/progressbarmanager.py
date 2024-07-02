from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

class ProgressBarManager:
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