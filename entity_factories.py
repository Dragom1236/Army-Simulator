from components.ai import HostileEnemy, RangedEnemy, HealingEnemy
from components.baseclass import Templar, Cleric, Archer, Shaman, Shadow, Assassin, NoClass
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    faction="Holy",
    Class=Templar(),
    Subclass=NoClass(),
    equipment=Equipment(),
    fighter=Fighter(hp=500, base_defense=30, base_power=50,mana=150,mana_regen=20),
    inventory=Inventory(capacity=26),
    level=Level(),
)

soldier = Actor(
    char="T",
    color=(255, 255, 255),
    name="Templar",
    ai_cls=HostileEnemy,
    faction="Holy",
    Class=Templar(),
    Subclass=Shadow(),
    equipment=Equipment(),
    fighter=Fighter(hp=150, base_defense=37, base_power=21,mana=5,mana_regen=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100, ),
)
soldier2 = Actor(
    char="S",
    color=(139, 0, 0),
    name="Shadow",
    ai_cls=HostileEnemy,
    faction="Dark",
    Class=Shadow(),
    Subclass=NoClass(),
    equipment=Equipment(),
    fighter=Fighter(hp=210, base_defense=7, base_power=50,mana=15,mana_regen=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=150),
)

archer = Actor(
    char="A",
    color=(255, 255, 1),
    name="Archer",
    ai_cls=RangedEnemy,
    faction="Holy",
    Class=Archer(),
    Subclass=NoClass(),
    equipment=Equipment(),
    fighter=Fighter(hp=100, base_defense=5, base_power=15, mana=50, mana_regen=8),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=250, ),

)

Assassin = Actor(
    char="A",
    color=(1, 1, 1),
    name="Assassin",
    ai_cls=HostileEnemy,
    faction="Dark",
    Class=Assassin(),
    Subclass=NoClass(),
    equipment=Equipment(),
    fighter=Fighter(hp=50, base_defense=0, base_power=25,mana=30,mana_regen=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=275, )

)

Cleric = Actor(
    char="C",
    color=(220, 220, 1),
    name="Cleric",
    ai_cls=HealingEnemy,
    faction="Holy",
    Class=Cleric(),
    Subclass=NoClass(),
    equipment=Equipment(),
    fighter=Fighter(hp=50, base_defense=15, base_power=25,mana=100,mana_regen=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=500, )
)

Shaman = Actor(
    char="S",
    color=(128, 0, 128),
    name="Shaman",
    ai_cls=HealingEnemy,
    faction="Dark",
    Class=Shaman(),
    Subclass=NoClass(),
    equipment=Equipment(),
    fighter=Fighter(hp=50, base_defense=10, base_power=6,mana=50,mana_regen=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=500, )
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=120, radius=3),
)
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=100),
)
lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=200, maximum_range=5),
)

dagger = Item(
    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)
