# Local
from tinker.tinker_controller import TinkerController


class CacheController(TinkerController):

    def cache_clear(self, img_path=None):
        if not img_path:
            return "Please enter in a path."
        self.clear_image_cache(img_path)
        return 'Cache cleared for path, "' + img_path + '"'
