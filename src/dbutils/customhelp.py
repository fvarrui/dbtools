from argparse import HelpFormatter, SUPPRESS

class CustomHelpFormatter(HelpFormatter):
    """"
    "Custom HelpFormatter para remplazar 'usage:' por 'Uso:'"
    """

    def add_usage(self, usage, actions, groups, prefix='Uso: '):
        if usage is not SUPPRESS:
            args = usage, actions, groups, prefix
            self._add_item(self._format_usage, args)