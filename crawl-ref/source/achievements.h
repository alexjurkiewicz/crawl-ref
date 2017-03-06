#pragma once

#include "AppHdr.h"

#include "achievement-data.h"
#include "achievement-type.h"

bool have_achievement(achievement cheevo_id);
bool have_achievement(achievement_data cheevo);

void celebrate(achievement cheevo);
void reset_celebration(achievement cheevo_id);
