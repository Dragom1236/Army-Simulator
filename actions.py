from __future__ import annotations

from abc import ABC
from typing import Optional, Tuple, TYPE_CHECKING

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
            self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        if target.faction == self.entity.faction:
            return
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity.name == "Assassin":
            damage += self.entity.fighter.power
            attack_desc = f"{self.entity.name.capitalize()} stabs {target.name}, twice,"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
        if target.name == "Player":
            print(target.fighter.base_defense)
            print(self.entity.fighter.base_power)
        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
            KillConfirm(self.entity).resolve(self.entity, target)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class ActionWithTarget(Action, ABC):
    def __init__(self, entity: Actor, x: int, y: int) -> object:
        super().__init__(entity)

        self.x = x
        self.y = y

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine


class RangedAction(ActionWithTarget, ABC):
    def reform(self, x, y) -> None:
        target = self.engine.game_map.get_actor_at_location(x, y)
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        if target.faction == self.entity.faction:
            return
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} shot {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
            KillConfirm(self.entity).resolve(self.entity, target)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )

    @property
    def ranged_target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(self.targ_xy)

    @property
    def targ_xy(self, x, y) -> Tuple[int, int]:
        return self.x, self.y


class HealingAction(ActionWithTarget, ABC):
    def reform(self, x, y) -> None:
        target = self.engine.game_map.get_actor_at_location(x, y)
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        if target.faction != self.entity.faction:
            return
        healing = self.entity.fighter.power

        attack_desc = f"{self.entity.name.capitalize()} healed {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if healing > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {healing} hit points.", attack_color
            )
            target.fighter.hp += healing
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but their wounds do not recover.", attack_color
            )

    @property
    def ranged_target_actor(self) -> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(self.targ_xy)

    @property
    def targ_xy(self, x, y) -> Tuple[int, int]:
        return self.x, self.y


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)
        if self.entity.name == "Assassin":
            pass


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class KillConfirm(Action, ABC):
    def resolve(self, Actor1: Actor, Target: Actor):
        if Target.fighter.hp <= 0:
            kill_desc = f"{self.entity.name.capitalize()} has killed {Target.name}"
            print(kill_desc)
            if Actor1.name != "Player":
                no = Actor1.level.current_level
                xpqgiven = Target.level.xp_given / no
                xpqgiven = int(xpqgiven)
                print("Boi")
                Actor1.level.add_xp(xpqgiven)
                print(xpqgiven)
            else:
                print("Not Boi")
                Actor1.level.add_xp(Target.level.xp_given)
                print(Target.level.xp_given)
