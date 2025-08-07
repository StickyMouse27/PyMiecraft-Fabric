package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

public class NamedExecutor<T> extends TimedExecutor<T, NamedValue<Consumer<T>>, LinkedList<NamedValue<Consumer<T>>>> {
    public NamedExecutor(IntSupplier tickSupplier) {
        super(tickSupplier, LinkedList::new);
    }

    public void tick(T data, String name) {
        int currentTick = tickSupplier.getAsInt();
        LinkedList<NamedValue<Consumer<T>>> exes = scheduled.remove(currentTick);
        if (exes != null) {
            exes.forEach(callback -> {
                if (callback.name().equals(name))
                    callback.get().accept(data);
            });
        }
    }

    public void push(int tick, Consumer<T> callback, String name, TickType tickType) {
        super.push(tick, new NamedValue<>(callback, name), tickType);
    }
}
