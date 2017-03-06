#pragma once

#include <map>
#include <string>

#include "achievement-type.h"

enum class achievement_unlock_type
{
    normal,
    counter,
};

struct achievement_data
{
    string title;
    string description;
    achievement_unlock_type unlock_type;
    // For counter achievements, how many times do you need to 'celebrate'
    // the achievement before it's unlocked?
    int num_count;
};

// keep in sync with achievement in achievement-type.h
const map<achievement, achievement_data> achievements = {
    {
        achievement::enter_lair,
        { "Welcome to the Jungle", "Enter the Lair of the Beasts", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::first_blood,
        { "First Blood", "Kill a monster", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::pigmund,
        { "Pigmund!", "Polymorph Sigmund", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::hop,
        { "Hypothetically Optimal Player", "Attack a monster with bread", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::xomlucky,
        { "(Un)Lucky", "Pray at a faded altar and worship Xom", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::saint,
        { "Saint", "Die with six stars of piety", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::temple_of_doom,
        {
            "Temple of Doom",
            "Exit a rune floor with the rune and in sight of at least four enemies",
            achievement_unlock_type::normal,
            0,
        }
    },
    {
        achievement::streaker,
        { "Streaker", "Stairdance a bat", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::cleaning_crew,
        { "Cleaning Crew", "Kill a berserker ghost", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::yavp,
        { "YAVP", "Win the game", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::strike_out,
        { "Strike Out", "Miss three attacks in a row", achievement_unlock_type::counter, 3, }
    },
    {
        achievement::foolminant_prism,
        { "Foolminant Prism", "Destroy your own fulminant prism", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::daredevil,
        { "Daredevil", "Wall jump (with Wu Jian) over an Orb of Destruction", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::desperate_power,
        { "Desperate Power", "Reduce yourself to 1 hp with Sublimation of Blood", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::dogfight,
        { "Dogfight", "Kill a canine with another canine", achievement_unlock_type::normal, 0, }
    },
    {
        achievement::clarity,
        { "Clarity", "Confuse Crazy Yiuf", achievement_unlock_type::normal, 0, }
    },
};

// error: static_assert expression is not an integral constant expression
// COMPILE_CHECK((int)achievement::NUM_ACHIEVEMENTS == achievements.size());
