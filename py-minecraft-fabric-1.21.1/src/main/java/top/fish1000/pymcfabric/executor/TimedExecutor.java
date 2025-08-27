package top.fish1000.pymcfabric.executor;

import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.IntSupplier;
import java.util.function.Supplier;

public abstract class TimedExecutor<T, S extends Supplier<Consumer<T>>, L extends List<ExecutorIdentifier<S>>> {
    public enum TickType {
        RELATIVE, ABSOLUTE;

        public int convert(int tick, int currentTick) {
            return this == RELATIVE ? tick + currentTick : tick;
        }
    }

    protected final IntSupplier tickSupplier;
    protected final HashMap<Integer, L> callbackScheduled;
    protected final Supplier<L> listSupplier;

    public TimedExecutor(IntSupplier tickSupplier, Supplier<L> listSupplier) {
        this.tickSupplier = Objects.requireNonNull(tickSupplier);
        this.listSupplier = Objects.requireNonNull(listSupplier);
        this.callbackScheduled = new HashMap<>();
    }

    /**
     * 添加命令到指定tick
     * 
     * @param tick             添加的tick
     * @param callbackSupplier 命令
     * @param tickType         是否是相对tick
     */
    public int push(int tick, S callbackSupplier, TickType tickType) {
        int currentTick = tickSupplier.getAsInt();
        tick = tickType.convert(tick, currentTick);
        if (tick < currentTick) {
            throw new IllegalArgumentException("Cannot execute for past tick");
        }
        ExecutorIdentifier<S> id = ExecutorIdentifier.of(callbackSupplier);
        callbackScheduled.computeIfAbsent(tick, k -> listSupplier.get()).add(id);
        return id.id;
    }

    public void remove(int id) {
        callbackScheduled.values().forEach(list -> list.removeIf(callback -> callback.id == id));
    }

    /**
     * 执行当前tick的所有命令
     * 
     * @param data 数据
     */
    public void tick(T data) {
        int currentTick = tickSupplier.getAsInt();
        L exes = callbackScheduled.remove(currentTick);
        if (exes != null) {
            System.out.println("tick " + currentTick);
            exes.forEach(callback -> callback.get().get().accept(data));
        }
    }
}
