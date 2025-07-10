from robocasa.models.fixtures import Fixture


class DishRack(Fixture):
    """
    Dish Rack fixture class
    """

    def __init__(
        self,
        xml="fixtures/accessories/dish_racks/DishRack026",
        name="dish_rack",
        *args,
        **kwargs
    ):
        super().__init__(
            xml=xml, name=name, duplicate_collision_geoms=False, *args, **kwargs
        )

    def get_reset_region_names(self):
        return ("int_0", "int_1")

    @property
    def nat_lang(self):
        return "dish rack"
