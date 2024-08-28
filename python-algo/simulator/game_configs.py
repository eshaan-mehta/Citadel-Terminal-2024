configs = {
  "unitInformation": [
    {
      "name": "wall",
      "cost": 2.0,
      "getHitRadius":0.01,
      "startHealth":40.0,
      "unitCategory": 0,
      "refundPercentage": 0.75,
      "turnsRequiredToRemove": 1,
      "upgrade": {
        "startHealth": 120.0
      }
    },
    {
      "name": "support",
      "cost": 4.0,
      "getHitRadius":0.01,
      "shieldPerUnit":3.0,
      "shieldRange":2.5,
      "startHealth":20.0,
      "unitCategory": 0,
      "shieldBonusPerY": 0.0,
      "refundPercentage": 0.75,
      "shieldDecay": 0.0,
      "turnsRequiredToRemove": 1,
      "upgrade": {
        "shieldRange": 6,
        "shieldPerUnit": 5,
        "shieldBonusPerY": 0.3
      }
    },
    {
      "name": "turret",
      "attackDamageMobile":6.0,
      "cost":3.0,
      "getHitRadius":0.01,
      "attackRange":2.5,
      "startHealth":75.0,
      "unitCategory": 0,
      "refundPercentage": 0.75,
      "turnsRequiredToRemove": 1,
      "upgrade": {
        "cost": 5.0,
        "attackRange":4.5,
        "attackDamageMobile":14.0
      }
    },
    {
      "name": "scout",
      "attackDamageTower":2.0,
      "attackDamageMobile":2.0,
      "playerBreachDamage":1.0,
      "cost":1.0,
      "getHitRadius":0.01,
      "attackRange":4.5,
      "startHealth":12.0,
      "speed":1,
      "unitCategory": 1,
      "selfDestructDamageMobile": 15.0,
      "selfDestructDamageTower": 15.0,
      "spForBreach": 1.0,
      "selfDestructRange": 1.5,
      "selfDestructStepsRequired": 5
    },
    {
      "name": "demolisher",
      "attackDamageMobile":8.0,
      "attackDamageTower":8.0,
      "playerBreachDamage":2.0,
      "cost":3.0,
      "getHitRadius":0.01,
      "attackRange":4.5,
      "startHealth":5.0,
      "speed":0.5,
      "unitCategory": 1,
      "selfDestructDamageMobile": 5.0,
      "selfDestructDamageTower": 5.0,
      "spForBreach": 1.0,
      "selfDestructRange": 1.5,
      "selfDestructStepsRequired": 5
    },
    {
      "name": "interceptor",
      "attackDamageMobile":20.0,
      "playerBreachDamage":1.0,
      "cost":2.0,
      "getHitRadius":0.01,
      "attackRange":3.5,
      "startHealth":30.0,
      "speed":0.25,
      "unitCategory": 1,
      "selfDestructDamageMobile": 40.0,
      "selfDestructDamageTower": 40.0,
      "spForBreach": 1.0,
      "selfDestructRange": 1.5,
      "selfDestructStepsRequired": 5
    },
  ],
  "resources":{
    "turnIntervalForBitCapSchedule":10,
    "turnIntervalForBitSchedule":10,
    "bitRampBitCapGrowthRate":5.0,
    "roundStartBitRamp":10,
    "bitGrowthRate":1.0,
    "startingHP":30.0,
    "bitsPerRound":5.0,
    "coresPerRound":5.0,
    "coresForPlayerDamage":1.0,
    "bitDecayPerRound":0.25,
  },
}
