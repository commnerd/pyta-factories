from faker import Faker
import collections.abc


class Factory:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, faker):
        self.definitions = []
        self.states = []
        self.afterMaking = []
        self.afterCreating = []
        self.faker = Faker()

    def defineAs(self, cls, name, attr):
        return self.define(cls, attr, name)

    def define(self, cls, attr, name='default'):
        self.definitions[cls][name] = attr
        return self

    def state(self, cls, state, attr):
        self.states[cls][state] = attr
        return self

    def afterMaking(self, cls, callback, name='default'):
        self.afterMaking[cls][name] = callback
        return self

    def afterMakingState(self, cls, state, callback):
        return self.afterMaking(cls, callback, state)

    def afterCreating(self, cls, callback, name='default'):
        self.afterCreating[cls][name] = callback
        return self

    def afterCreatingState(self, cls, state, callback):
        return self.afterCreating(cls, callback, state)

    def create(self, cls, attr=[]):
        return self.of(cls).create(attr)

    def createAs(self, cls, name, attr=[]):
        return self.of(cls, name).create(attr)

    def make(self, cls, attr=[]):
        return self.of(cls).make(attr)

    def makeAs(self, cls, name, attr=[]):
        return self.of(cls, name).make(attr)

    def rawOf(self, cls, name, attr=[]):
        return self.raw(cls, attr, name)

    def raw(self, cls, attr=[], name='default'):
        return getattr(cls, self.definitions[cls][name])(**attr)

    def of(self, cls, name='default'):
        return FactoryBuilder(cls, name, self.definitions, self.states, self.afterMaking, self.afterCreating, self.faker)

    def offsetExists(self, offset):
        return bool(self.definitions[offset])

    def offsetGet(self, offset):
        return self.make(offset)

    def offsetSet(self, offset, value):
        self.define(offset, value)


class FactoryBuilder:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, cls, name, definitions, states, afterMaking, afterCreating, faker):
        self.name = name
        self.cls = cls
        self.faker = faker
        self.states = states
        self.definitions = definitions
        self.afterMaking = afterMaking
        self.afterCreating = afterCreating

    def times(self, amount):
        self.amount = amount
        return self

    def state(self, state):
        return self.states([state])

    def states(self, states):
        # $this->activeStates = is_array($states) ? $states : func_get_args();
        # self.activeStates = isinstance(states) ? states :
        return self

    def connection(self, name):
        self.connection = name
        return self

    def lazy(self, attr=[]):
        return lambda: self.create(attr)

    def create(self, attr=[]):
        results = self.make(attr)

        # if ($results instanceof Model) {
        #     $this->store(collect([$results]));

        #     $this->callAfterCreating(collect([$results]));
        # } else {
        #     $this->store($results);

        #     $this->callAfterCreating($results);
        # }

        self.store(results)
        self.callAfterCreating(results)

        return results

    def store(self, results):
        for model in results:
            if not bool(self.connection):
                model.setConnection(model.newQueryWithoutScopes().getConnection() -> getName())
            model.save()

    def make(self, attr=[]):
        if self.amount == None:
            return tap(self.makeInstance(attr), lambda instance: self.callAfterMaking([instance]))

        # if ($this->amount < 1) {
        #     return (new $this->class)->newCollection();
        # }
        if self.amount < 1:
            return (self.cls)()

        # $instances = (new $this->class)->newCollection(array_map(function () use ($attributes) {
        #     return $this->makeInstance($attributes);
        # }, range(1, $this->amount)));
        instances = []
        self.callAfterMaking(instances)

        return instances

    def raw(self, attr=[]):
        if self.amount == None:
            return self.getRawAttributes(attr)

        if self.amount < 1:
            return []

        # return array_map(function () use ($attributes) {
        #     return $this->getRawAttributes($attributes);
        # }, range(1, $this->amount));
        return []

    def getRawAttributes(self, attr=[]):
        # if (! isset($this->definitions[$this->class][$this->name])) {
        #     throw new InvalidArgumentException("Unable to locate factory with name [{$this->name}] [{$this->class}].");
        # }

        # $definition = call_user_func(
        #     $this->definitions[$this->class][$this->name],
        #     $this->faker, $attributes
        # );

        # return $this->expandAttributes(
        #     array_merge($this->applyStates($definition, $attributes), $attributes)
        # );
        return attr

    def makeInstance(self, attr=[]):
        # return Model::unguarded(function () use ($attributes) {
        #     $instance = new $this->class(
        #         $this->getRawAttributes($attributes)
        #     );

        #     if (isset($this->connection)) {
        #         $instance->setConnection($this->connection);
        #     }

        #     return $instance;
        # });
        instance = (self.cls)(self.getRawAttributes(attr))

        return instance

    def applyStates(self, definition, attr=[]):
        for state in self.activeStates:
            if not bool(self.states[self.cls][state]):
                if self.stateHasAfterCallback(state):
                    continue

                raise Exception(
                    "Unable to locate [{$state}] state for [{$this->class}].")

            # $definition = array_merge(
            #     $definition,
            #     $this->stateAttributes($state, $attributes)
            # );
        return definition

    def stateAttributes(self, state, attr=[]):
        stateAttributes = self.states[self.cls][state]

        # if not is_callable(stateAttributes):
        #     return stateAttributes

        return getattr(stateAttributes, self.faker)(**attr)

    def expandAttributes(self, attr):
        for attribute in attr:
            # if is_callable(attribute) and not is_string(attribute) and not is_array(attribute):
            #     attribute = attribute(attributes)

            # if isinstance(attribute, staticmethod):
            #     attribute = attribute.create().getKey()

            # if isinstance(attribute, Model):
            #     attribute = attribute.getKey()
            attribute = attribute

        return attr

    def callAfterMaking(self, models):
        self.callAfter(self.afterCreating, models)

    def callAfter(afterCallbacks, models):
        # $states = array_merge([$this->name], $this->activeStates);

        # $models->each(function ($model) use ($states, $afterCallbacks) {
        #     foreach ($states as $state) {
        #         $this->callAfterCallbacks($afterCallbacks, $model, $state);
        #     }
        # });
        return

    def callAfterCallbacks(self, afterCallbacks, model, state):
        # if (! isset($afterCallbacks[$this->class][$state])) {
        #     return;
        # }

        # foreach ($afterCallbacks[$this->class][$state] as $callback) {
        #     $callback($model, $this->faker);
        # }
        return

    def stateHasAfterCallback(self, state):
        return bool(self.afterMaking[self.cls][state]) or bool(self.afterCreating[self.cls][state])


def factory(model):
    return Factory(model)
