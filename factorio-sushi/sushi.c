#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#include "../macros.h"

typedef int32_t Value;

/* Tick-by-tick simulation of sushi belt circuit network */
/* Sushi belt : keep in memory amount of items present and maximum capacity, allow or disallow adding more based on current counts */

/* First : we'll do a science */

// todo: simulate production shortages

#define LAB_COUNT 24
#define LAB_TICKS_PER_SCIENCE 120
#define BELT_CAPACITY 8
#define BELT_COUNT (LAB_COUNT * 8)
#define SCIENCE_TYPE_COUNT ((Value)(sizeof(BeltState) / sizeof(Value)))

#define MIN_VALUE_PER_SCIENCE (BELT_COUNT * BELT_CAPACITY / SCIENCE_TYPE_COUNT)

typedef struct {
    Value red, green, gray, blue, purple, yellow, white;
} BeltState;

int main()
{
    BeltState state = {0};

    Value ticksSinceLastLabConsumption = 0;
    
    long tickCount = 0;

    while (true) {
        // Print state
        printf("%ld.", tickCount);
        for (int i = 0; i < SCIENCE_TYPE_COUNT; ++i) {
            printf(" %3d", *((Value*)&state + i));
        }

        // Lab consumption
        if (ticksSinceLastLabConsumption == 0) {
            if (state.red > 0
                && state.green > 0
                && state.gray > 0
                && state.blue > 0
                && state.purple > 0
                && state.yellow > 0
                && state.white > 0) {
                state.red -= LAB_COUNT;
                state.green -= LAB_COUNT;
                state.gray -= LAB_COUNT;
                state.blue -= LAB_COUNT;
                state.purple -= LAB_COUNT;
                state.yellow -= LAB_COUNT;
                state.white -= LAB_COUNT;
            }
            ticksSinceLastLabConsumption = LAB_TICKS_PER_SCIENCE;
        } else {
            --ticksSinceLastLabConsumption;
        }

        // Refurbishment
        if (state.red < MIN_VALUE_PER_SCIENCE) ++state.red;
        if (state.green < MIN_VALUE_PER_SCIENCE) ++state.green;
        if (state.gray < MIN_VALUE_PER_SCIENCE) ++state.gray;
        if (state.blue < MIN_VALUE_PER_SCIENCE) ++state.blue;
        if (state.purple < MIN_VALUE_PER_SCIENCE) ++state.purple;
        if (state.yellow < MIN_VALUE_PER_SCIENCE) ++state.yellow;
        if (state.white < MIN_VALUE_PER_SCIENCE) ++state.white;

        ++tickCount;
        getchar();
    }
}
