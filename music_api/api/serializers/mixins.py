
class ContextUtilsMixin:
    """ Caution: for serializers using data from request. Such serializers shouldnt be used for validate  """
    @property
    def request_kwargs(self):
        try:
            return self.context.get('request').parser_context.get('kwargs')
        except AttributeError:
            return None

    @property
    def current_basename(self):
        try:
            return self.context.get('request').parser_context.get('view').basename
        except AttributeError:
            return ''

    def get_album_id(self):
        """ Returns value from URL request if it exists """
        if self.current_basename.endswith('albums') and self.request_kwargs.get('pk'):
            return self.request_kwargs.get('pk')
        try:
            return next(value for key, value in self.request_kwargs.items() if key.endswith('albums_pk'))
        except StopIteration:
            return None

    def get_artist_id(self):
        """ Returns value from request URL if it exists """
        if self.current_basename.endswith('artists') and self.request_kwargs.get('pk'):
            return self.request_kwargs.get('pk')
        try:
            return next(value for key, value in self.request_kwargs.items() if key.endswith('artists_pk'))
        except (StopIteration, AttributeError):
            return None
