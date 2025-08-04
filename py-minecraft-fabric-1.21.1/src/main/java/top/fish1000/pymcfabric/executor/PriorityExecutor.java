package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class PriorityExecutor<T>
        extends TimedExecutor<T, PriorityValue<Consumer<T>>, LinkedList<PriorityValue<Consumer<T>>>> {

    PriorityExecutor(Supplier<Integer> tickSupplier) {
        super(tickSupplier, LinkedList::new);
    }

    public void push(int tick, int priority, Consumer<T> callback, TickType tickType) {
        push(tick, new PriorityValue<>(priority, callback), tickType);
    }

    public void tick(T data) {
        int currentTick = tickSupplier.get();
        LinkedList<PriorityValue<Consumer<T>>> toRun = scheduled.get(currentTick);
        toRun.sort((a, b) -> a.priority() - b.priority());
        scheduled.replace(currentTick, toRun);
        super.tick(data);
    }
}
