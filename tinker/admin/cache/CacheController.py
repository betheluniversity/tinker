from tinker.tinker_controller import TinkerController
from tinker import tools


class CacheController(TinkerController):

    def cache_clear(self, img_path=None):
        if not img_path:
            return "Please enter in a path."
        return tools.clear_image_cache(img_path)