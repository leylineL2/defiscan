import unittest
import action
from action import SwapDeposit, SwapWithDraw
import logging
from logging import Logger,DEBUG
from decimal import Decimal

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler())
logger.addFilter(DEBUG)

class TestSwapDeposit(unittest.TestCase):
    def setUp(self) -> None:
        action._clear_lp()
        return super().setUp()
    def convert_coin(self,amount:Decimal):
        return Decimal(f"{10**6}") * amount

    def create_deposit_event(self,a_amount,b_amount,share):
        event = [
            {"type": "swap_deposit",
            "attributes": [
                {"key": "pool_id",
                "value": "ukava:usdx"},
                {"key": "amount",
                "value": f"{a_amount}ukava,{b_amount}usdx"},
                {"key": "shares",
                "value": f"{share}"}
            ]},
        ]
        return event
    def create_withdraw_event(self,a_amount,b_amount,share):
        event = [
            {"type": "swap_withdraw",
            "attributes": [
                {"key": "pool_id",
                "value": "ukava:usdx"},
                {"key": "amount",
                "value": f"{a_amount}ukava,{b_amount}usdx"},
                {"key": "shares",
                "value": f"{share}"}
            ]},
        ]
        return event

    def test_collect(self):
        events_a = [
            {"type": "swap_deposit",
            "attributes": [
                {"key": "pool_id",
                "value": "ukava:usdx"},
                {"key": "amount",
                "value": "10000ukava,10000usdx"},
                {"key": "shares",
                "value": "10000"}
            ]},
        ]

        result = SwapDeposit(events_a,0)
        print(result)
        events_b = [
            {"type": "swap_withdraw",
            "attributes": [
                {"key": "pool_id",
                "value": "ukava:usdx"},
                {"key": "amount",
                "value": "10000ukava,10000usdx"},
                {"key": "shares",
                "value": "10000"}]}
        ]
        SwapWithDraw(events_b,0)

    def test_LP(self):
        print("-"*20)
        coin_ukava = self.convert_coin(Decimal('10'))
        coin_usdx = self.convert_coin(Decimal('10'))
        share = 1000000
        events_a = self.create_deposit_event(coin_ukava,coin_usdx,share)

        result = SwapDeposit(events_a,0)
        print(f"lp: {action.swp_lp_amount}")
        print(events_a)
        coin_ukava = self.convert_coin(Decimal('4'))
        coin_usdx = self.convert_coin(Decimal('6'))
        ratio = Decimal("0.5")
        events_b = self.create_withdraw_event(coin_ukava,coin_usdx,share*ratio)
        print(events_b)
        print(f"share2 {share*ratio}")
        kava_expect = ((ratio) * Decimal('10')) - Decimal("4")
        print(f"expect: {kava_expect}")
        result = SwapWithDraw(events_b,0)
        print(result)
        # ukava: 10 * 0.5 - 4 = 1 LOSS
        # usdx: 10 * 0.5 - 6 = 1 BONUS
        self.assertEqual(result[0]['Base'],'KAVA')
        self.assertEqual(result[0]['Action'],'LOSS')
        self.assertEqual(result[0]['Volume'],Decimal('1.0'))
        self.assertEqual(result[1]['Base'],'USDX')
        self.assertEqual(result[1]['Action'],'BONUS')
        self.assertEqual(result[1]['Volume'],Decimal('1.0'))

    def test_LP2(self):
        print("-"*20)
        coin_ukava = self.convert_coin(Decimal('100'))
        coin_usdx = self.convert_coin(Decimal('100'))
        share = 1000000
        events_a = self.create_deposit_event(coin_ukava,coin_usdx,share)

        print(events_a)
        result = SwapDeposit(events_a,0)

        coin_ukava = self.convert_coin(Decimal('40'))
        coin_usdx = self.convert_coin(Decimal('60'))
        ratio = Decimal("0.5")
        events_b = self.create_withdraw_event(coin_ukava,coin_usdx,share*ratio)


        result = SwapWithDraw(events_b,0)
        print(result)
        print(f"lp: {action.swp_lp_amount}")

        # ukava: 100 * 0.5:50 - 40 = 10 LOSS
        # usdx: 100 * 0.5 - 60 = 10 BONUS
        self.assertEqual(result[0]['Base'],'KAVA')
        self.assertEqual(result[0]['Action'],'LOSS')
        self.assertEqual(result[0]['Volume'],Decimal('10.0'))
        self.assertEqual(result[1]['Base'],'USDX')
        self.assertEqual(result[1]['Action'],'BONUS')
        self.assertEqual(result[1]['Volume'],Decimal('10.0'))

        coin_ukava = self.convert_coin(Decimal('60'))
        coin_usdx = self.convert_coin(Decimal('40'))
        ratio = Decimal("0.5")
        events_b = self.create_withdraw_event(coin_ukava,coin_usdx,share*ratio)

        coin_ukava = self.convert_coin(Decimal('50'))
        coin_usdx = self.convert_coin(Decimal('50'))
        share = 500000
        events_a = self.create_deposit_event(coin_ukava,coin_usdx,share)

        print(events_a)
        result = SwapDeposit(events_a,0)
        # ukava: 60 + 50 = 110
        # usdx: 40 + 50 = 90
        # share 500000 + 500000 = 100000
        self.assertEqual(action.swp_lp_amount['ukava:usdx']['KAVA'],Decimal('110'))
        self.assertEqual(action.swp_lp_amount['ukava:usdx']['USDX'],Decimal('90'))
        self.assertEqual(action.swp_lp_amount['ukava:usdx']['shares'],Decimal('1000000.0'))

        result = SwapWithDraw(events_b,0)
        print(result)
        # ukava: 110 * 0.5:55 - 60 = 5 BONUS
        # usdx: 90 * 0.5:45 - 40 = 5 LOSS
        self.assertEqual(result[0]['Base'],'KAVA')
        self.assertEqual(result[0]['Action'],'BONUS')
        self.assertEqual(result[0]['Volume'],Decimal('5.0'))
        self.assertEqual(result[1]['Base'],'USDX')
        self.assertEqual(result[1]['Action'],'LOSS')
        self.assertEqual(result[1]['Volume'],Decimal('5.0'))
        # self.assertEqual(result,[])
        # print(f"lp: {action.swp_lp_amount}")
        # self.assertEqual(action.swp_lp_amount['ukava:usdx']['shares'],Decimal('0'))
        # self.assertEqual(action.swp_lp_amount['ukava:usdx']['KAVA'],Decimal('0'))
        # self.assertEqual(action.swp_lp_amount['ukava:usdx']['USDX'],Decimal('0'))



if __name__ == "__main__":
    unittest.main()