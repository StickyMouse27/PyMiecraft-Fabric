package top.fish1000.pymcfabric.executor;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

import top.fish1000.pymcfabric.PymcMngr;

public class NamedAdvancedExecutor<T> extends NamedExecutor<T> {

    protected final LinkedList<NamedExecutorIdentifier<Consumer<T>>> callbackContinuousList;
    protected final LinkedList<NamedExecutorIdentifier<Consumer<T>>> callbackOnceList;
    protected final LinkedList<Integer> toRemove;
    protected final LinkedList<NamedExecutorIdentifier<Consumer<T>>> toAddContinuous;
    protected final LinkedList<NamedExecutorIdentifier<Consumer<T>>> toAddOnce;
    protected final LinkedList<Pair<Integer, NamedExecutorIdentifier<Consumer<T>>>> toAddScheduled;
    protected Boolean removeAllContinuous = false;
    protected Boolean removeAllOnce = false;
    protected Boolean removeAllScheduled = false;

    protected int tick = 0;
    protected Long tickTimeSum = 0L;
    protected HashMap<String, Long> tickTimes = new HashMap<>();
    protected Boolean printDebug = false;

    public NamedAdvancedExecutor(IntSupplier tickSupplier) {
        super(tickSupplier);
        callbackContinuousList = new LinkedList<>();
        callbackOnceList = new LinkedList<>();
        toRemove = new LinkedList<>();
        toAddContinuous = new LinkedList<>();
        toAddOnce = new LinkedList<>();
        toAddScheduled = new LinkedList<>();
    }

    @Override
    public void tick(T data, String name) {
        // Utils.LOGGER.trace("Looking for callback: tick{} @ {}", tickSupplier.get(),
        // name);
        toRemove.forEach(id -> {
            callbackContinuousList.removeIf(callback -> callback.id == id);
            callbackOnceList.removeIf(callback -> callback.id == id);
            remove(id);
        });
        toRemove.clear();

        if (removeAllScheduled) {
            removeAll();
            removeAllScheduled = false;
        }
        if (removeAllOnce) {
            callbackOnceList.clear();
            removeAllOnce = false;
        }
        if (removeAllContinuous) {
            callbackContinuousList.clear();
            removeAllContinuous = false;
        }

        callbackContinuousList.addAll(toAddContinuous);
        toAddContinuous.clear();
        callbackOnceList.addAll(toAddOnce);
        toAddOnce.clear();
        toAddScheduled.forEach(id -> {
            push(id.first(), id.second(), TickType.RELATIVE);
        });
        toAddScheduled.clear();

        super.tick(data, name);
        callbackContinuousList.forEach(callback -> {
            if (callback.name.equals(name)) {
                PymcMngr.LOGGER.trace("Found callback(continuous) tick{} @ {}", tickSupplier.getAsInt(), name);
                callback.data.accept(data);
            }
        });
        callbackOnceList.forEach(callback -> {
            if (callback.name.equals(name)) {
                callback.data.accept(data);
                PymcMngr.LOGGER.trace("Found callback(once), removed tick{} @ {}", tickSupplier.getAsInt(), name);
            }
        });
        callbackOnceList.removeIf(nv -> nv.name.equals(name));
    }

    public void timedTick(T data, String name) {
        if (tick != tickSupplier.getAsInt()) {
            if (printDebug) {
                PymcMngr.LOGGER.info("Pymc tick time: {}ms @ tick{}", tickTimeSum / 1e6d, tick);
                tickTimes.forEach((n, t) -> PymcMngr.LOGGER.info("| {}ms @ {}", t / 1e6d, n));
                PymcMngr.LOGGER.info("+---------------------------------------------------------------->");
                printDebug = false;
            }
            if (tickTimeSum > 40e6) {
                PymcMngr.LOGGER.warn("Tick time too long(shouldn't longer than 40ms): {}ms @ tick{}",
                        tickTimeSum / 1e6d, tick);
            }
            tick = tickSupplier.getAsInt();
            tickTimeSum = 0L;
            tickTimes.clear();
        }
        long startTime = System.nanoTime();
        tick(data, name);
        long tickTime = System.nanoTime() - startTime;
        if (tickTime > 1e4) {
            tickTimes.put(name, tickTime);
        }
        tickTimeSum += tickTime;
    }

    public void printDebug() {
        printDebug = true;
    }

    public void tryTick(T data, String name) {
        try {
            timedTick(data, name);
        } catch (Exception e) {
            callbackContinuousList.clear();
            callbackOnceList.clear();
            callbackScheduled.clear();
            PymcMngr.LOGGER.error("Error in callback, skipped, callback list cleared: tick{} @ {}",
                    tickSupplier.getAsInt(), name);
            e.printStackTrace();
        }
    }

    public int pushScheduled(int tick, Consumer<T> callback, String name) {
        PymcMngr.LOGGER.trace("Pushing callback(scheduled): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        toAddScheduled.add(Pair.of(tick, id));
        return id.id;
    }

    public void removeScheduledAll() {
        PymcMngr.LOGGER.trace("Removing all callback(scheduled)");
        removeAllScheduled = true;
    }

    public int pushOnce(Consumer<T> callback, String name) {
        PymcMngr.LOGGER.trace("Pushing callback(once): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        toAddOnce.add(id);
        return id.id;
    }

    public void removeOnceAll() {
        PymcMngr.LOGGER.trace("Removing all callback(once)");
        removeAllOnce = true;
    }

    public int pushContinuous(Consumer<T> callback, String name) {
        PymcMngr.LOGGER.trace("Pushing callback(continuous): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        toAddContinuous.add(id);
        return id.id;
    }

    public void removeContinuousAll() {
        PymcMngr.LOGGER.trace("Removing all callback(continuous)");
        removeAllContinuous = true;
    }

    public void ezRemove(int id) {
        PymcMngr.LOGGER.trace("Removing callback id: {}", id);
        toRemove.add(id);
    }

    public void ezRemoveAll() {
        removeScheduledAll();
        removeOnceAll();
        removeContinuousAll();
    }
}
