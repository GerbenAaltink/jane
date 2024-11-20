import time


class Duration(object):

    _duration_depth = -1
    _uid = 0
    _time_totals = {}

    

    def get_uid(self):
        Duration._uid += 1
        return Duration._uid
    def get_duration_depth(self):
        Duration._duration_depth += 1
        return Duration._duration_depth

    def clear_duration_depth(self):
        Duration._duration_depth -= 1
        return Duration._duration_depth

    def __init__(self, title):
        self.uid = self.get_uid()
        self.title = title 
        self.start = None
        self.finish = None
        self.duration = None
        self.depth = None
        self.steps = []
    async def __aenter__(self):
        self.depth = self.get_duration_depth()
        self.start = time.time()

        return self 

    def __call__(self, title):
        step = Duration(title)
        self.steps.append(step)
        return step

    def update_globals(self):
        if self.title not in Duration._time_totals:
            Duration._time_totals[self.title] = dict(
                time_average=0,
                time_total=0,
                times_executed=0
            )
        Duration._time_totals[self.title]['times_executed'] += 1
        Duration._time_totals[self.title]['time_total'] += self.duration
        Duration._time_totals[self.title]['time_average'] = Duration._time_totals[self.title]['times_executed'] / Duration._time_totals[self.title]['time_total']



    async def __aexit__(self, *args, **kwargs):
        self.finish = time.time()
        self.duration = self.finish - self.start
        if args != (None,None,None) or kwargs:
            print(args)
            print(kwargs)
            exit(1)
        self.update_globals()
       
    def dump(self,depth=0):
        print(" " * depth,end="")
        print(" - ",end="")
        print("{} {} took {}s".format(self.uid,self.title, self.duration))
        for step in self.steps:
            step.dump(depth+1)

    def __enter__(self):
        self.start = time.time() 
        return self 

    def __exit__(self, *args, **kwargs):
        self.finish = time.time()
        self.duration = self.finish - self.start
        self.update_globals()


def durations_dump():
    for title, data in Duration._time_totals.items():
        print(title,end=': ')
        print(data)
