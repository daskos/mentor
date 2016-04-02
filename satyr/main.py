from __future__ import absolute_import, division, print_function



from .native import Scheduler
from .utils import catch, set_signals, run_daemon


class Test(Scheduler):

    def match(self, offers):
        return {} # mappings

    def on_offers(self, driver, offers):
        #print(driver)
        #print(offers)

        to_launch = self.match(offers)
        to_decline = [o for o in offers if o not in to_launch]

        for offer, tasks in to_launch.items():
            driver.launch(offer, tasks, filters=None)  # filters?

        for offer in to_decline:  # decline remaining unused offers
            driver.decline(offer)




if __name__ == '__main__':
    fw = Test(name='pinasen')
    run_daemon('Mesos Test Framework', fw)
