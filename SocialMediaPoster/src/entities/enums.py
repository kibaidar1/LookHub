import enum


class GenderEnum(enum.Enum):
    """Enumeration for clothing gender categories.
    
    Represents the target gender for clothing items with Russian labels.
    
    Values:
        male (str): "мужской" - For men's clothing and looks
        female (str): "женский" - For women's clothing and looks
        unisex (str): "унисекс" - For unisex clothing and looks
    """
    male = "мужской"
    female = "женский"
    unisex = "унисекс"

    def __str__(self):
        return self.name


class ColourEnum(enum.Enum):
    """Enumeration for clothing colors.
    
    Represents available colors for clothing items with Russian labels.
    
    Values:
        white (str): "белый"
        beige (str): "бежевый"
        gray (str): "серый"
        red (str): "красный"
        pink (str): "розовый"
        orange (str): "оранжевый"
        yellow (str): "желтый"
        green (str): "зеленый"
        light_blue (str): "голубой"
        blue (str): "синий"
        purple (str): "фиолетовый"
        brown (str): "коричневый"
        black (str): "черный"
    """
    white = "белый"
    beige = "бежевый"
    gray = "серый"
    red = "красный"
    pink = "розовый"
    orange = "оранжевый"
    yellow = "желтый"
    green = "зеленый"
    light_blue = "голубой"
    blue = "синий"
    purple = "фиолетовый"
    brown = "коричневый"
    black = "черный"

    def __str__(self):
        return self.name
