package top.fish1000.pymcfabric.executor;

import java.util.LinkedList;
import java.util.function.Consumer;
import java.util.function.IntSupplier;

import com.ibm.icu.impl.Pair;

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
        // Utils.LOGGER.info("Looking for callback: tick{} @ {}", tickSupplier.get(),
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
            push(id.first, id.second, TickType.RELATIVE);
        });
        toAddScheduled.clear();

        super.tick(data, name);
        callbackContinuousList.forEach(callback -> {
            if (callback.name.equals(name)) {
                PymcMngr.LOGGER.info("Found callback(continuous) tick{} @ {}", tickSupplier.getAsInt(), name);
                callback.data.accept(data);
            }
        });
        callbackOnceList.forEach(callback -> {
            if (callback.name.equals(name)) {
                callback.data.accept(data);
                PymcMngr.LOGGER.info("Found callback(once), removed tick{} @ {}", tickSupplier.getAsInt(), name);
            }
        });
        callbackOnceList.removeIf(nv -> nv.name.equals(name));
    }

    public void tryTick(T data, String name) {
        try {
            tick(data, name);
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
        PymcMngr.LOGGER.info("Pushing callback(scheduled): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        toAddScheduled.add(Pair.of(tick, id));
        return id.id;
    }

    public void removeScheduledAll() {
        PymcMngr.LOGGER.info("Removing all callback(scheduled)");
        removeAllScheduled = true;
    }

    public int pushOnce(Consumer<T> callback, String name) {
        PymcMngr.LOGGER.info("Pushing callback(once): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        toAddOnce.add(id);
        return id.id;
    }

    public void removeOnceAll() {
        PymcMngr.LOGGER.info("Removing all callback(once)");
        removeAllOnce = true;
    }

    public int pushContinuous(Consumer<T> callback, String name) {
        PymcMngr.LOGGER.info("Pushing callback(continuous): tick{} @ {}", tickSupplier.getAsInt(), name);
        NamedExecutorIdentifier<Consumer<T>> id = new NamedExecutorIdentifier<>(callback, name);
        toAddContinuous.add(id);
        return id.id;
    }

    public void removeContinuousAll() {
        PymcMngr.LOGGER.info("Removing all callback(continuous)");
        removeAllContinuous = true;
    }

    public void ezRemove(int id) {
        PymcMngr.LOGGER.info("Removing callback id: {}", id);
        toRemove.add(id);
    }

    public void ezRemoveAll() {
        removeScheduledAll();
        removeOnceAll();
        removeContinuousAll();
    }
}
