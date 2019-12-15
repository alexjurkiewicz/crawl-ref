/**
 * @file
 * @brief Magical anvils.
**/

#include "AppHdr.h"

#include "anvil.h"

#include "env.h"
#include "invent.h"
#include "item-status-flag-type.h"
#include "item-use.h"
#include "makeitem.h"
#include "message.h"
#include "output.h"
#include "player-equip.h"
#include "terrain.h"
#include "view.h"

/**
 * Use a magical anvil.
 *
 * @returns whether the anvil was used.
 */
void use_anvil()
{
    ASSERT(grd(you.pos()) == DNGN_ENCHANTED_ANVIL);

    int item_slot;
    item_def itemp;
    bool is_armour;
    bool is_weapon;
    while (true)
    {
        // If this is changed to allow more than weapon/armour, a lot of the
        // below code will need to be updated.
        item_slot = prompt_invent_item("Enchant what?", menu_type::invlist,
                                        OSEL_ANVIL_ENCHANTABLE, OPER_ANY,
                                        invprompt_flag::escape_only);
        if (prompt_failed(item_slot))
        {
            canned_msg(MSG_OK);
            return;
        }

        itemp = you.inv[item_slot];
        is_armour = itemp.base_type == OBJ_ARMOUR;
        is_weapon = itemp.base_type == OBJ_WEAPONS;

        if (!is_armour && !is_weapon) {
          canned_msg(MSG_UNTHINKING_ACT);
          return;
        }

        // If the item is equipped, tell the player to unequip it
        if (is_armour && item_is_worn(item_slot))
        {
            mpr("You need to take that off first!");
            return;
        }
        else if (is_weapon && you.equip[EQ_WEAPON] == item_slot)
        {
          mpr("You need to unwield that first!");
          return;
        }

        // If the item is an unrand, enchanting it will fail
        if (itemp.flags & ISFLAG_UNRANDART)
        {
            canned_msg(MSG_UNTHINKING_ACT);
            continue;
        }

        break;
    }

    item_def &item = itemp;

    const char *item_name = item.name(DESC_YOUR).c_str();
    mprf("You place your %s on the anvil...", item_name);
    const int beneficial = x_chance_in_y(4, 5);
    const int delta = min(1, binomial(6, 30));
    const COLOURS colour = beneficial ? YELLOW : GREEN;
    const char *spirit = beneficial ? "a helpful" : "an evil";
    const char *verb = beneficial ? "gained" : "lost";
    mprf("You sense %s spirit.", spirit);
    flash_view_delay(UA_PLAYER, colour, 300);
    item.plus += beneficial ? delta : -delta;
    mprf("Your %s has %s enchantment!", item_name, verb);

    you.inv[item_slot] = item;

    // Destroy the anvil
    mpr("The anvil dulls and falls dormant.");
    auto const pos = you.pos();
    dungeon_terrain_changed(pos, DNGN_DESTROYED_ANVIL);
    view_update_at(pos);

    redraw_screen();
    you.turn_is_over = true;
    return;
}
