package top.fish1000.pymcfabric.executor;

import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Supplier;

public class TimedExecutor<T, S extends Supplier<Consumer<T>>, L extends List<S>> {
    public enum TickType {
        RELATIVE, ABSOLUTE;

        public int convert(int tick, int currentTick) {
            return this == RELATIVE ? tick + currentTick : tick;
        }
    }

    protected final Supplier<Integer> tickSupplier;
    protected final HashMap<Integer, L> scheduled;
    protected final Supplier<L> listSupplier;

    public TimedExecutor(Supplier<Integer> tickSupplier, Supplier<L> listSupplier) {
        this.tickSupplier = Objects.requireNonNull(tickSupplier);
        this.listSupplier = Objects.requireNonNull(listSupplier);
        this.scheduled = new HashMap<>();
    }

    /**
     * 添加命令到指定tick
     * 
     * @param tick             添加的tick
     * @param callbackSupplier 命令
     * @param tickType         是否是相对tick
     */
    public void push(int tick, S callbackSupplier, TickType tickType) {
        int currentTick = tickSupplier.get();
        tick = tickType.convert(tick, currentTick);
        if (tick < currentTick) {
            throw new IllegalArgumentException("Cannot execute for past tick");
        }
        scheduled.computeIfAbsent(tick, k -> listSupplier.get()).add(callbackSupplier);
    }

    /**
     * 执行当前tick的所有命令
     * 
     * @param data 数据
     */
    public void tick(T data) {
        int currentTick = tickSupplier.get();
        L exes = scheduled.remove(currentTick);
        if (exes != null) {
            exes.forEach(callback -> callback.get().accept(data));
        }
    }
}
