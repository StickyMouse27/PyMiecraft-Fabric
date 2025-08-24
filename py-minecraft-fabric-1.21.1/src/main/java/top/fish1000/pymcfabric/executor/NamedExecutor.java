package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

public class NamedExecutor<T>
        extends
        TimedExecutor<T, NamedExecutorIdentifier<Consumer<T>>, LinkedList<ExecutorIdentifier<NamedExecutorIdentifier<Consumer<T>>>>> {
    public NamedExecutor(IntSupplier tickSupplier) {
        super(tickSupplier, LinkedList::new);
    }

    public void tick(T data, String name) {
        int currentTick = tickSupplier.getAsInt();
        LinkedList<ExecutorIdentifier<NamedExecutorIdentifier<Consumer<T>>>> exes = callbackScheduled
                .remove(currentTick);
        if (exes != null) {
            exes.forEach(callback -> {
                if (callback.get().name.equals(name))
                    callback.get().get().accept(data);
            });
        }
    }

    public int push(int tick, Consumer<T> callback, String name, TickType tickType) {
        return super.push(tick, new NamedExecutorIdentifier<>(callback, name), tickType);
    }
}
