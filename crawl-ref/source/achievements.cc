#include <map>
#include <string>

#include "achievements.h"

#include "achievement-data.h"
#include "achievement-type.h"
#include "message.h" // mprf
#include "mpr.h" // more
#include "stringutil.h" // make_stringf

const int _COUNTER_ACHIEVEMENT_ALREADY_UNLOCKED = -1;

// Get the achievement_data struct
static achievement_data _achievement_data(achievement cheevo_id)
{
    return achievements.find(cheevo_id)->second;
}

static string _achievement_prop_name(achievement_data cheevo)
{
    return make_stringf("cheevo_%s", cheevo.title.c_str());
}

static void _message_unlock(achievement_data cheevo)
{
    mprf("<red>Achievement unlocked!</red> <green>%s</green> <blue>(%s)</blue>",
            cheevo.title.c_str(),
            cheevo.description.c_str());
    more();
}

static void _unlock_normal_achievement(achievement_data cheevo)
{
    you.props[_achievement_prop_name(cheevo)] = true;
    _message_unlock(cheevo);
}

static void _maybe_unlock_counter_achievement(achievement_data cheevo)
{
    const string prop_name = _achievement_prop_name(cheevo);
    const int current_count = you.props[prop_name];
    if (current_count == _COUNTER_ACHIEVEMENT_ALREADY_UNLOCKED)
        return;
    if ((current_count + 1) >= cheevo.num_count)
    {
        you.props[prop_name] = _COUNTER_ACHIEVEMENT_ALREADY_UNLOCKED;
        _message_unlock(cheevo);
    }
    else
        you.props[prop_name] = current_count + 1;
}

bool have_achievement(achievement cheevo_id)
{
    const achievement_data cheevo = _achievement_data(cheevo_id);
    return have_achievement(cheevo);
}

bool have_achievement(achievement_data cheevo)
{
    switch (cheevo.unlock_type)
    {
        case achievement_unlock_type::normal:
            return you.props[_achievement_prop_name(cheevo)].get_bool();
        case achievement_unlock_type::counter:
            return you.props[_achievement_prop_name(cheevo)].get_int()
                   == _COUNTER_ACHIEVEMENT_ALREADY_UNLOCKED;
                }
}

void celebrate(achievement cheevo_id)
{
    const achievement_data cheevo = _achievement_data(cheevo_id);

    if (have_achievement(cheevo_id))
        return;

    if (cheevo.unlock_type == achievement_unlock_type::normal)
        _unlock_normal_achievement(cheevo);
    else if (cheevo.unlock_type == achievement_unlock_type::counter)
        _maybe_unlock_counter_achievement(cheevo);
}

// For achievements which have a counter, reset the counter to 0
void reset_celebration(achievement cheevo_id)
{
    const achievement_data cheevo = _achievement_data(cheevo_id);
    ASSERT(cheevo.unlock_type == achievement_unlock_type::counter);
    const string prop_name = _achievement_prop_name(cheevo);
    const int current_count = you.props[prop_name];
    if (current_count == _COUNTER_ACHIEVEMENT_ALREADY_UNLOCKED)
        return;
    you.props[prop_name] = 0;
}
