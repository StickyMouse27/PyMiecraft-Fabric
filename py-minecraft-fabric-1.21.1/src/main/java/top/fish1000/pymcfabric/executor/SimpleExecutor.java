package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class SimpleExecutor<T> extends TimedExecutor<T, Supplier<Consumer<T>>, LinkedList<Supplier<Consumer<T>>>> {
    public SimpleExecutor(Supplier<Integer> tickSupplier) {
        super(tickSupplier, LinkedList::new);
    }

    public void push(int tick, Consumer<T> callback, TickType tickType) {
        push(tick, () -> callback, tickType);
    }
}
