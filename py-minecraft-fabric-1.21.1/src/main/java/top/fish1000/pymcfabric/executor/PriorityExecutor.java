package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

public class PriorityExecutor<T>
        extends
        TimedExecutor<T, PriorityValue<Consumer<T>>, LinkedList<ExecutorIdentifier<PriorityValue<Consumer<T>>>>> {

    PriorityExecutor(IntSupplier tickSupplier) {
        super(tickSupplier, LinkedList::new);
    }

    public void push(int tick, int priority, Consumer<T> callback, TickType tickType) {
        push(tick, new PriorityValue<>(priority, callback), tickType);
    }

    public void tick(T data) {
        int currentTick = tickSupplier.getAsInt();
        LinkedList<ExecutorIdentifier<PriorityValue<Consumer<T>>>> toRun = callbackScheduled.get(currentTick);
        toRun.sort((a, b) -> a.get().priority() - b.get().priority());
        callbackScheduled.replace(currentTick, toRun);
        super.tick(data);
    }
}
